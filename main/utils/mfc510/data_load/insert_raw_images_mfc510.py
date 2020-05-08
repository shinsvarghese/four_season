"""
Insert mfc510 images (bin files) to mongoDB for existing documents.
It will put image meta under 'image.raw'
If we do not find image for timestamp it will 'continue'. (do nothing)

You can choose and modify config params in/from 'config.py' file.
"""

import os

from mongodb_pipeline.mfc510.utils.mfc510_util import mfc510_raw_meta

from mongodb_pipeline.utils.general import get_params, validate_params
from mongodb_pipeline.utils.general import get_hash_from_bytes, parallel_process
from mongodb_pipeline.utils.general import create_chunks, merge_list_w_dict
from mongodb_pipeline.utils.general import get_logger, params_to_logformat

from mongodb_pipeline.mfc510.data_load.config import mfc510_sample_noannot
from mongodb_pipeline.mfc510.utils.query_templates import q_img_exists
from mongodb_pipeline.utils.mongo_manager import MongoManager

logger = get_logger()


def process(params):
    """ Process for inserting a batch of raw (bin) images to mongoDB.

    :param params: dict, config parameters
    """
    mongo_man = MongoManager(params["params"])
    for _id in params["ids"]:
        collentry = mongo_man.collection.find_one({"_id": _id["_id"]})
        timestamp = collentry["timestamp"]
        img_path = os.path.join(params["params"]["img_dir"], str(timestamp) + ".bin")
        if not os.path.isfile(img_path):
            continue

        with open(img_path, mode='rb') as file:
            raw_file = file.read()

        raw_hashid = get_hash_from_bytes(raw_file)
        raw_meta = mfc510_raw_meta
        raw_meta["hash"] = raw_hashid
        if "image" in collentry:
            collentry["image"]["raw"] = raw_meta
        else:
            collentry["image"] = {"raw": raw_meta}

        f_name = "raw_" + str(collentry["sourcefile"]).replace('.rrec', '').replace('.rec', '')
        f_name += "-" + str(collentry["timestamp"]) + ".bin"

        mongo_man.write_file_to_gridfs(file_content=raw_file, f_name=f_name,
                                       _id=raw_hashid, content_type="image/bin")
        mongo_man.collection.update_one({"_id": collentry["_id"]},
                                        {"$set": {"image": collentry["image"]}})


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
    params = get_params(mfc510_sample_noannot)
    validate_params(params, ['uri', 'db', 'coll', 'gridfs', 'processes', 'img_dir'])
    mongo_man = MongoManager(params)

    query = q_img_exists(False)
    ids = mongo_man.get_ids(query)
    number_of_docs = len(ids)
    print(number_of_docs)
    log_before_execute(params, query, number_of_docs)

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
