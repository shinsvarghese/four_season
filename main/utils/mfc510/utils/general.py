import time
import cv2
import hashlib
import numpy as np
from optparse import OptionParser
import pymongo
from gridfs import GridFS

from contextlib import contextmanager
import os, io, sys, glob
import tempfile
import ctypes
import logging
import multiprocessing
import re


def format_float_in_standard_form(f):
    s = str(f)
    m = re.match(r'(-?)(\d)(?:\.(\d+))?e([+-]\d+)', s)
    if not m:
        return s
    sign, intpart, fractpart, exponent = m.groups('')
    exponent = int(exponent) + 1
    digits = intpart + fractpart
    if exponent < 0:
        return sign + '0.' + '0'*(-exponent) + digits
    exponent -= len(digits)
    return sign + digits + '0'*exponent + '.0'


def setup_user_credential(user_list=None):
    if user_list is None:
        user_list = ['writeMfc520_test_labels', 'write_recording_noannot', 'read']

    from pypwd import PasswordManager
    pm = PasswordManager()
    pm.set_users_password(user_list)


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    log_dir = '.'
    makedir_if_not_exists(log_dir)
    # create a file handler
    handler = logging.FileHandler(os.path.join(log_dir, 'Chips.log'))
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s; %(filename)s; %(levelname)s; %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)
    return logger


def params_to_logformat(params):
    ret = ''
    for key in params:
        if str(key).lower() == 'uri':
            uri = params[key]
            try:
                password = uri[uri.rfind(':') + 1:uri.rfind('@')]
            except ValueError:
                password = ""
            ret += key + ': ' + uri.replace(password, 'password')
        elif str(key).lower() == 'pw' or str(key).lower() == 'password':
            ret += key + ': {}'.format('password')
        else:
            ret += key + ': ' + str(params[key]) + ', '

    return ret[:-2]


def makedir_if_not_exists(out_dir):
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)


class FILE(ctypes.Structure):
    _fields_ = [
        ("_ptr", ctypes.c_char_p),
        ("_cnt", ctypes.c_int),
        ("_base", ctypes.c_char_p),
        ("_flag", ctypes.c_int),
        ("_file", ctypes.c_int),
        ("_charbuf", ctypes.c_int),
        ("_bufsize", ctypes.c_int),
        ("_tmpfname", ctypes.c_char_p),
    ]


@contextmanager
def stdout_redirector(stream):
    # Gives you the name of the library that you should really use (and then load through ctypes.CDLL
    libc = ctypes.cdll.msvcrt
    iob_func = libc.__iob_func
    iob_func.restype = ctypes.POINTER(FILE)
    iob_func.argtypes = []

    array = iob_func()
    c_stdout = ctypes.addressof(array[1])

    # The original fd stdout points to. Usually 1 on POSIX systems.
    original_stdout_fd = sys.stdout.fileno()

    def _redirect_stdout(to_fd):
        """Redirect stdout to the given file descriptor."""
        # Flush the C-level buffer stdout
        #libc.fflush(c_stdout)
        # Make original_stdout_fd point to the same file as to_fd
        os.dup2(to_fd, original_stdout_fd)

    # Save a copy of the original stdout fd in saved_stdout_fd
    saved_stdout_fd = os.dup(original_stdout_fd)
    try:
        # Create a temporary file and redirect stdout to it
        tfile = tempfile.TemporaryFile(mode='w+b')
        _redirect_stdout(tfile.fileno())
        # Yield to caller, then redirect stdout back to the saved fd
        yield
        _redirect_stdout(saved_stdout_fd)
        # Copy contents of temporary file to the given stream
        tfile.flush()
        tfile.seek(0, io.SEEK_SET)
        stream.write(tfile.read())
    finally:
        tfile.close()
        os.close(saved_stdout_fd)


def show_image(img_data, img_name='test_img', wait_ms=0):
    cv2.imshow(img_name, img_data)
    cv2.waitKey(wait_ms)
    cv2.destroyAllWindows()


def show_y_and_rgb(image_output):
    for out in image_output:
        if out["channel"] == "y":
            channel_y = out["data"]
            show_image(channel_y * 16, "chips_Y")
        if out["channel"] == "u":
            channel_u = out["data"]
        if out["channel"] == "v":
            channel_v = out["data"]

    rgb = yuv2rgb(channel_y, channel_u, channel_v)
    show_image(rgb, "rgb")


def save_image(img_data, out_path='test_img.png'):
    cv2.imwrite(out_path, img_data)


def get_hash_from_bytes(data):
    return hashlib.md5(data).hexdigest()


def standardize_yuv(y, u, v):
    return np.dstack((
        y / 16,
        cv2.resize(u, y.shape[::-1], interpolation=cv2.INTER_LINEAR),
        cv2.resize(v, y.shape[::-1], interpolation=cv2.INTER_LINEAR)
    )).astype(np.uint8)


def yuv2rgb(y, u, v):
    yuv = standardize_yuv(y, u, v)
    return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)


def convert_image_to_numpy_array(img_data, is_uint16):
    img_data = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_UNCHANGED)
    uint_type = np.uint16 if is_uint16 else np.uint8

    return np.asarray(img_data).astype(uint_type)


def parallel_process(func, args, num_workers, return_needed=False):
    pool = multiprocessing.Pool(num_workers)
    if return_needed:
        ret = pool.map(func, args)
    else:
        pool.map(func, args)
        ret = None

    pool.terminate()
    pool.join()

    return ret


def create_chunks(list_to_chunk, num_workers, min_chunk_size=5):
    """This function chunk a list to 'smaller' lists.
    Something like this your_list_to_chunk=[1, 2, 3, 4, ... 9] -> [[1,2,3], [4,5,6], [7,8,9]]

    :param list_to_chunk: a list, what you want to divide to chunks
    :param num_workers: number of parallel processes/workers you will be execute
    :param min_chunk_size: the minimum size of your chunk(s)
    :return: chunked list
    :rtype: list of lists
    """
    if num_workers <= 0:
        # we would like to avoid division by zero
        num_workers = 2
    chunk_size = max(int(len(list_to_chunk) / num_workers), min_chunk_size)
    return [list_to_chunk[i:i + chunk_size] for i in range(0, len(list_to_chunk), chunk_size)]


def merge_list_w_dict(your_list, your_dict, list_tag="ids", dict_tag="params"):
    """ This function merge a list with a dictionary & return a list containing dictionaries.

    Return something like this:
    [{"ids": your_list[0], "params": your_dict}, {"ids": your_list[1], "params": your_dict} ...]

    :param your_list: list
    :param your_dict: dict
    :param list_tag: str
    :param dict_tag: str
    :return: list containing dictionaries.
    """
    return [{list_tag: item, dict_tag: your_dict} for item in your_list]


def connect_to_mongo(conn_params):
    client = pymongo.MongoClient(conn_params["uri"])
    db = client[conn_params['db']]
    collection = db[conn_params['coll']]
    try:
        db.command('ping')
    except Exception as e:
        raise Exception("MongoDB is not running. {}".format(e))

    return collection, GridFS(db, conn_params['gridfs'])


def read_file_to_list(file_path):
    with open(file_path, 'r') as myfile:
        rec_paths = myfile.read().splitlines()
        return list(set(rec_paths))


def list_folder_names(parent_dir_path):
    return [name for name in os.listdir(parent_dir_path) if
            os.path.isdir(os.path.join(parent_dir_path, name))]


def check_folder_path(folder_path):
    if not folder_path.endswith("/*") and not folder_path.endswith("\\*"):
        if folder_path.endswith("/") or folder_path.endswith("\\"):
            return folder_path + '*'
        else:
            return folder_path + '/*'

    return folder_path


def get_file_names_in_folder(folder_path, full_path=True):
    file_paths = glob.glob(check_folder_path(folder_path))
    if full_path:
        return file_paths
    return [os.path.basename(x) for x in file_paths]


def get_filtered_img_paths(params, raw_file_extend):
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


# TODO: maybe it should be depricated
def check_img_dict(imgdict):
    if not imgdict.endswith("/*") and not imgdict.endswith("\\*"):
        if imgdict.endswith("/") or imgdict.endswith("\\"):
            return imgdict + '*'
        else:
            return imgdict + '/*'

    return imgdict


def validate_params(params, required_params=[]):
    for required_param in required_params:
        if required_param not in params:
            raise Exception('"{}" parameter is required'.format(required_param))

    if "y_level" in params and params["y_level"] not in [2, 3, 4, 5, 6]:
        raise Exception("y_level parameter is not valid (2, 3, 4, 5, 6)")

    if "uv_level" in params and params["uv_level"] not in [3, 4, 5, 6]:
        raise Exception("uv_level parameter is not valid (3, 4, 5, 6)")

    if "slope" in params and params["slope"] not in [0, 1]:
        raise Exception("slope parameter is not valid (day=0, night=1)")


def get_params(default_params):
    if len(sys.argv) > 1:
        return parse_args_to_dict()
    else:
        return default_params


def parse_args_to_dict():
    parser = OptionParser()
    parser.add_option("--uri", dest="uri", help="source mongodb URI like mongodb://user:pass@hostname")
    parser.add_option("--d", dest="db_name", help="source mongodb database name")
    parser.add_option("--c", dest="collection_name", help="source mongodb collection name")
    parser.add_option("--g", "--gridfs", dest="gridfs", default="image_data", help="name of the gridfs on mongodb")
    parser.add_option("--sourcefile", dest="sourcefile", help="name of (r)rec file (in MongoDB)")
    parser.add_option("--version", dest="version", help="dll version tag, is added as suffix in mongodb chips/cipp key")
    parser.add_option("--y_level", dest="y_level", help="required Y pyramid level (2, 3, 4, 5, 6)", type="int")
    parser.add_option("--uv_level", dest="uv_level", help="required UV pyramid level (3, 4, 5, 6)", type="int")
    parser.add_option("--slope", dest="slope", help="slope, day=0, night=1", type="int")
    parser.add_option("--sourcedirectory", dest="sourcedirectory",
                      help="source directory, the folder where you store binary images (.bin)")

    parser.add_option("--img_dir", dest="img_dir", help="folder path for images")

    parser.add_option("--frequency", dest="frequency", default=4,
                      help="frequency of sample rate, e.g. if it is 3 it will load every 3th images to mongodb",
                      type="int")
    parser.add_option("-p", "--pool", dest="processes", default=6,
                      help="number of parallel processes to be used", type="int")
    parser.add_option("--proc_type", dest="proc_type", default="chips",
                      help="processing type could either be 'cipp1' or 'chips'")

    (options, args) = parser.parse_args()
    return vars(options)


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print(method.__name__, ' ran for:', round((te - ts), 1), 's')
        return result

    return timed
