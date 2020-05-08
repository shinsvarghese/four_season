"""
Run chips for stereo depth estimation, mfc4xx images.
It will create y, u, v images from raw image (id on gridfs: 'image.[left/right].raw.hash')
It will create y, u, v tags (meta) under 'image.[left/right]' & load images (y, u,v) to gridfs.

You can choose and modify config params in/from 'config.py' file.
"""

import os
import time
import ctypes
import numpy as np
import cv2
import _ctypes

from mongodb_pipeline.mfc510.utils.mfc510_util import mfc510_pyramid_levels_y
from mongodb_pipeline.mfc510.utils.mfc510_util import mfc510_pyramid_levels_uv
from mongodb_pipeline.mfc510.utils.mfc510_util import get_image_format
from mongodb_pipeline.utils.general import get_hash_from_bytes, show_y_and_rgb, get_params

from mongodb_pipeline.utils.general import validate_params, parallel_process
from mongodb_pipeline.utils.general import create_chunks, merge_list_w_dict
from mongodb_pipeline.utils.general import get_logger, params_to_logformat
from mongodb_pipeline.utils.general import convert_image_to_numpy_array

from mongodb_pipeline.mfc510.chips.config import mfc4xx_depth_latest
from mongodb_pipeline.utils.mongo_manager import MongoManager
from mongodb_pipeline.mfc510.utils.query_templates import mfc4xx_chips_depth

debug = 0
logger = get_logger()
CHIPS_DLL_NAME = "CHIPS510.dll"


def get_dll_path(is_licensed):
    """ This function set (and return w/) dll path.
    Based on config (is_licensed) it decides whether to use the licensed or the free version.
    It will add the proper dll folder to path and change the working directory.
    (It is necessary for dll license handling.)

    :param is_licensed: int 0 or 1
    :return: str the absolute path of chips dll file
    """
    if is_licensed:
        dll_folder = os.path.join(os.path.dirname(__file__), "..", "dll", "licensed")
        dll_folder = os.path.abspath(dll_folder)
        print('you will use licensed version of dll.')
    else:
        dll_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dll", "free"))
        print('you will use free version of dll.')

    dll_path = os.path.join(dll_folder, CHIPS_DLL_NAME)
    os.environ['PATH'] = dll_folder + ';' + os.environ['PATH']
    os.chdir(dll_folder)
    return dll_path


def write_images_to_mongodb(imgs, mongo_man, collentry, version, channel):
    """  Write chips (y, u, v) images to mongoDB with metadata

    :param imgs: list containing y, u, v images and their metadata
    :param mongo_man: mongoDB manager object
    :param collentry: dict containing current mongoDB doc metadata
    :param version: str version of chips coming from user config usually empty string ("") or "2"
    :param channel: str "left" or "right"
    """
    for img in imgs:
        enc_img = cv2.imencode(".png", img["data"])[1].tostring()
        hash_id = get_hash_from_bytes(enc_img)
        doc = {
            "slope": img["slope"],
            "hash": hash_id,
            "size_x": img["data"].shape[1],
            "size_y": img["data"].shape[0],
            "dll_version": img["dll_version"],
            "chips_version": version,
            "shift_x": 12,
            "shift_y": 0,
            "scale_x": 1.0 if img["channel"] == 'y' else 0.5,
            "scale_y": 1.0 if img["channel"] == 'y' else 0.5
        }

        collentry["image"][channel][img["channel"]] = {"chips" + version + "p" + str(img["level"]): doc}

        f_name = img["channel"] + "_" + channel + str(img["level"]) + "_" + version + "_"
        f_name += str(collentry["sourcefile"]).replace('.rrec', '').replace('.rec', '') + "-"
        f_name += str(collentry["timestamp"]) + "_" + str(img["slope"]) + ".png"

        mongo_man.write_file_to_gridfs(file_content=enc_img, f_name=f_name,
                                       _id=hash_id, content_type="image/png")
        mongo_man.collection.update_one({"_id": collentry["_id"]},
                                        {"$set": {"image": collentry["image"]}})


def call_dll(params, image_format, img_data=None):
    """ Generate chips (y, u, v) images with dll, from raw (bin) image data.

    :param params: dict, config parameters: y-uv level, slope, dll path etc.
    :param img_data: raw image from gridfs
    :return: list, containing y, u, v images and their metadata
    """
    width_out_y = mfc510_pyramid_levels_y['y' + str(params["params"]["y_level"])]['width']
    height_out_y = mfc510_pyramid_levels_y['y' + str(params["params"]["y_level"])]['height']
    width_out_uv = mfc510_pyramid_levels_uv['uv' + str(params["params"]["uv_level"])]['width']
    height_out_uv = mfc510_pyramid_levels_uv['uv' + str(params["params"]["uv_level"])]['height']

    # init output arrays
    image_out_y = ctypes.create_string_buffer(2000 * 1500 * 2)
    image_out_u = ctypes.create_string_buffer(2000 * 1500 * 1)
    image_out_v = ctypes.create_string_buffer(2000 * 1500 * 1)

    chips_dll = ctypes.CDLL(params['params']['dll_path'])

    start = time.time()
    chips_dll.runChips(ctypes.c_int(int(image_format)),
                       ctypes.c_char_p(img_data),
                       ctypes.c_int(int(params["params"]["slope"])),
                       ctypes.pointer(image_out_y),
                       ctypes.c_int(int(params["params"]["y_level"])),
                       ctypes.pointer(image_out_u),
                       ctypes.pointer(image_out_v),
                       ctypes.c_int(int(params["params"]["uv_level"])))

    elapsed_time = time.time() - start

    chips_dll.getVersion.restype = ctypes.c_char_p
    chips_cp_ver_no = chips_dll.getVersion().decode('utf-8')
    chips_dll.getLocalVersion.restype = ctypes.c_char_p
    dll_version = chips_dll.getLocalVersion().decode('utf-8')

    out_base_dict = {"slope": params["params"]["slope"],
                     "is_licensed": params['params']['is_licensed'],
                     "chips_cp_ver_no": chips_cp_ver_no,
                     "dll_version": str(dll_version)}

    # print(dll_version, chips_cp_ver_no, elapsed_time)

    out = list()
    out_y = np.frombuffer(image_out_y, np.uint16)
    out_y = out_y[:height_out_y * width_out_y].reshape((height_out_y, width_out_y))
    out.append(
        {"data": out_y, "channel": "y", "level": params["params"]["y_level"], **out_base_dict})

    out_u = np.frombuffer(image_out_u, np.uint8)
    out_u = out_u[:height_out_uv * width_out_uv].reshape((height_out_uv, width_out_uv))
    out.append(
        {"data": out_u, "channel": "u", "level": params["params"]["uv_level"], **out_base_dict})

    out_v = np.frombuffer(image_out_v, np.uint8)
    out_v = out_v[:height_out_uv * width_out_uv].reshape((height_out_uv, width_out_uv))
    out.append(
        {"data": out_v, "channel": "v", "level": params["params"]["uv_level"], **out_base_dict})

    # Release the dll
    lib_handle = chips_dll._handle
    del chips_dll
    _ctypes.FreeLibrary(lib_handle)
    try:
        _ctypes.FreeLibrary(lib_handle)
    except:
        pass

    if elapsed_time < 3:
        raise Exception("There might be some error, processing was too fast: " + str(elapsed_time))

    return out


def process(params):
    """ Process for executing a batch of chips generation.

    :param params: dict, config parameters
    """
    mongo_man = MongoManager(params["params"])
    for _id in params["ids"]:
        collentry = mongo_man.collection.find_one({"_id": _id["_id"]})

        if "camera_daytime" in collentry and collentry["camera_daytime"].lower() == "day":
            params["params"]["slope"] = 0
        elif "camera_daytime" in collentry and collentry["camera_daytime"].lower() == "night":
            params["params"]["slope"] = 1

        if "image" in collentry:
            gridfs_file_id = collentry["image"][params["params"]["channel"]]["raw"]["hash"]
            img_binary = mongo_man.read_file_content_from_gridfs(gridfs_file_id)
            image_format = get_image_format(img_binary)

            if image_format:
                img_binary = convert_image_to_numpy_array(img_binary, True).tobytes()

            if img_binary is not None:
                image_output = call_dll(params,
                                        image_format,
                                        img_data=img_binary
                                        )

                if debug:
                    show_y_and_rgb(image_output)
                    exit(1)
                else:
                    write_images_to_mongodb(image_output, mongo_man,
                                            collentry, params["params"]["version"],
                                            params["params"]["channel"])
            else:
                print("no image found in gridfs!")


def log_before_execute(params, query, number_of_docs):
    """ Log process params (config), query and number of docs (to process).

    :param params: dict, config parameters
    :param query: dict, a mongoDB query
    :param number_of_docs: int
    """
    logger.info('params: %s', params_to_logformat(params))
    logger.info('querry: %s', query)
    logger.info('docs to process: %d', number_of_docs)


def main():
    """ Main function
    """
    params = get_params(mfc4xx_depth_latest)
    validate_params(params, ['uri', 'db', 'coll', 'gridfs',
                             'version', 'y_level', 'uv_level',
                             'slope', 'is_licensed', 'processes'])

    params['dll_path'] = get_dll_path(params['is_licensed'])

    mongo_man = MongoManager(params)
    query = mfc4xx_chips_depth(params["channel"])
    ids = mongo_man.get_ids({})
    number_of_docs = len(ids)
    print(number_of_docs)
    log_before_execute(params, query, number_of_docs)
    # exit()

    chunked_ids = create_chunks(ids, params["processes"])
    process_params = merge_list_w_dict(chunked_ids, params, "ids", "params")

    if params["processes"] <= 1:
        for ids in chunked_ids:
            process({"ids": ids, "params": params})
    else:
        parallel_process(process, process_params, params["processes"])

    ids = mongo_man.get_ids(query)
    logger.info('number of docs left: %d', len(ids))


if __name__ == "__main__":
    main()
