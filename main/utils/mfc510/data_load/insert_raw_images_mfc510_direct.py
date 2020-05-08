"""
Insert mfc510 images (bin files) to mongoDB.
It will create new documents for every image.
It will put image meta under 'image.raw' & load bin file to gridfs (id: 'image.raw.hash')
If doc already exits it will 'continue'. (do nothing)

You can choose and modify config params in/from 'config.py' file.
"""

import os

from mongodb_pipeline.mfc510.utils.mfc510_util import mfc510_raw_meta

from mongodb_pipeline.utils.general import get_params, validate_params
from mongodb_pipeline.utils.general import parallel_process, create_chunks
from mongodb_pipeline.utils.general import merge_list_w_dict, get_logger
from mongodb_pipeline.utils.general import params_to_logformat, get_file_names_in_folder
from mongodb_pipeline.utils.general import get_hash_from_bytes, list_folder_names

from mongodb_pipeline.mfc510.data_load.config import mfc510_sample_noannot
from mongodb_pipeline.utils.mongo_manager import MongoManager

debug = 1
logger = get_logger()


def process(params):
    """ Process for inserting a batch of raw (bin) images to mongoDB.

    :param params: dict, config parameters
    """
    mongo_man = MongoManager(params["params"])
    sourcefile = params["params"]["sourcefile"]
    if not sourcefile.endswith('rec'):
        sourcefile += '.rrec'

    for image_path in params["image_paths"]:
        timestamp = os.path.splitext(os.path.basename(image_path))[0]  # get timestamp from filename

        # TODO: if doc_id concept will change it should be fixed/change as well
        doc_id = sourcefile + '_' + str(timestamp)
        current_doc = mongo_man.collection.find_one({"_id": doc_id})
        # when document already exists we don't want to insert it again
        if current_doc is not None:
            print("{} already exists!".format(doc_id))
            continue

        with open(image_path, mode='rb') as file:
            binfile_content = file.read()

        raw_hashid = get_hash_from_bytes(binfile_content)
        raw_meta = {"raw": mfc510_raw_meta}
        raw_meta["raw"]["hash"] = raw_hashid

        camera_daytime = "day" if params["params"]["slope"] == 0 else "night"
        i_doc = {"_id": sourcefile + '_' + str(timestamp),
                 "sourcefile": sourcefile,
                 "timestamp": int(timestamp),
                 "camera_daytime": camera_daytime,
                 "image": raw_meta
                 }

        f_name = sourcefile + "-" + str(timestamp) + "_" + str(params["params"]["slope"]) + ".bin"
        mongo_man.write_file_to_gridfs(file_content=binfile_content, f_name=f_name, _id=raw_hashid,
                                       content_type="image/bin")
        mongo_man.collection.update({"_id": i_doc["_id"]}, i_doc, upsert=True)


def get_filtered_img_paths(params, raw_file_extend='.bin'):
    """ This function collects image paths from params["img_dir"] folder
    filter for file extend, sample them by params["frequency"] and sort.

    :param params: dict, config parameters
    :param raw_file_extend: str, extend of raw file e.g.: .bin, .png
    :return: list, image paths (full/abs path)
    """
    image_paths = get_file_names_in_folder(params["img_dir"])
    image_paths = list(filter(lambda x: x.endswith(raw_file_extend), image_paths))
    image_paths.sort()
    return image_paths[0::params["frequency"]]


def log_before_execute(params, number_of_images):
    """  Log process params (config) and number of images (to process/upload).

    :param params: dict, config parameters
    :param number_of_images:
    """
    logger.info('params: %s', params_to_logformat(params))
    logger.info('images to process: %d', number_of_images)


def load_one_folder(params):
    """ Load one image folder (bin files) to mongoDB

    :param params: dict, config parameters
    """
    filtered_image_paths = get_filtered_img_paths(params)
    number_of_images = len(filtered_image_paths)
    print(number_of_images)

    log_before_execute(params, number_of_images)

    chunked_image_paths = create_chunks(filtered_image_paths, params["processes"])
    process_params = merge_list_w_dict(chunked_image_paths, params, "image_paths", "params")

    if params["processes"] <= 1:
        for image_path in chunked_image_paths:
            process({"image_paths": image_path, "params": params})
    else:
        parallel_process(process, process_params, params["processes"])


def load_folders(params):
    """ It will load bin files from subfolder to mongoDB.
    You have to set a parent folder in params['img_dir']
    It will 'walk' through your sub folders and collect bin files.
    Make sure that your sub-folder names are proper (r)rec file names.

    :param params:
    """
    dir_list = list_folder_names(params['img_dir'])
    base_dir = params['img_dir']
    for cur_dir in dir_list:
        params['img_dir'] = base_dir + cur_dir
        params['sourcefile'] = os.path.basename(os.path.dirname(params['img_dir']))
        load_one_folder(params)


def main():
    """ Main function
    """
    params = get_params(mfc510_sample_noannot)
    validate_params(params, ['uri', 'db', 'coll', 'gridfs',
                             'img_dir', 'slope', 'sourcefile',
                             'frequency', 'processes'])

    load_one_folder(params)


if __name__ == "__main__":
    main()
