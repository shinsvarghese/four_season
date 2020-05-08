import cv2
import numpy as np
import pymongo
from gridfs import GridFS


class MongoManager:
    def __init__(self, conn_params={}, ldap=False):
        """ initialize your MongoManager object & if you provide
        connection params it will connect to mongoDB.

        :param conn_params: dict it should contain the following parameters (keys):
               'db', 'coll', 'gridfs', & ('uri' or 'host', 'user', 'pw' (password))
        :param ldap: True or False whether to login/connect w/ ldap/windows credentials.
        """
        if conn_params is None or conn_params == {}:
            return

        if ldap:
            self.ldap_connect(conn_params)
            return

        self.connect(conn_params)
    def terminate_connection(self):
        self.client.close()

    def connect(self, conn_params):
        """ Connect to mongoDB based on connection params,
        & it sets the attributes (client, db, gridfs etc.)

        :param conn_params: dict, it should contain the following parameters (keys):
               'db', 'coll', 'gridfs', & ('uri' or 'host', 'user', 'pw' (password))
        """
        try:
            self.client = pymongo.MongoClient(conn_params["uri"])
        except Exception:
            self.client = pymongo.MongoClient(conn_params['host'])
            self.client.admin.authenticate(conn_params['user'], conn_params['pw'])

        try:
            self.set_db(conn_params['db'])
            self.set_collection(conn_params['coll'])
            self.set_gridfs(conn_params['gridfs'])
        except KeyError:
            pass

    def connect2(self, host, db_name, collection_name, gridfs_name, usr, pwd):
        self.client = pymongo.MongoClient(host, unicode_decode_error_handler="ignore")

        if usr != '' and pwd != '':
            self.client.admin.authenticate(usr, pwd)

        try:
            self.set_db(db_name)
            self.set_collection(collection_name)
            self.set_gridfs(gridfs_name)
        except KeyError:
            pass

    def ldap_connect(self, conn_params, ssl=False):
        """Connect to mongoDB via ldap. (w/ windows credentials)

        :param conn_params:
        :param ssl: True or False
        """
        try:
            self.client = pymongo.MongoClient(
                conn_params["uri"] + '/{}?authSource=$external&authMechanism=PLAIN&ssl={}'
                .format(conn_params['db'], str(ssl).lower()))
        except Exception as e:
            print('putty: {}'.format(e))
            self.client = pymongo.MongoClient(conn_params['host'], ssl=ssl)
            self.client.admin.authenticate(conn_params['user'], conn_params['pw'],
                                           source="$external", mechanism="PLAIN")

        try:
            self.set_db(conn_params['db'])
            self.set_collection(conn_params['coll'])
            self.set_gridfs(conn_params['gridfs'])
        except KeyError:
            pass

    def ldap_connect2(self, host, port, user, passw, db_name,
                      collection_name, gridfs_name, ssl=False):
        self.client = pymongo.MongoClient(host, port, ssl=ssl)
        self.client.admin.authenticate(user, passw, source="$external", mechanism="PLAIN")

        try:
            self.set_db(db_name)
            self.set_collection(collection_name)
            self.set_gridfs(gridfs_name)
        except KeyError:
            pass

    def set_db(self, db_name):
        self.db = self.client[db_name]

    def set_collection(self, collection_name):
        self.collection = self.db[collection_name]

    def set_gridfs(self, gridfs_name):
        self.gridfs = GridFS(self.db, gridfs_name)

    def read_file_content_from_gridfs(self, _id):
        return self.gridfs.get(_id).read()

    def write_file_to_gridfs(self, file_content, f_name, _id, content_type):
        if self.gridfs.exists(_id):
            print('id: {} already exists on gridfs'.format(str(_id)))
            # self.gridfs.delete(_id)
            return

        self.gridfs.put(file_content, _id=_id, filename=f_name, content_type=content_type)
        if not self.gridfs.exists(_id):
            raise Exception('write file to gridfs failed')

    def upload(self, file_content, **kwargs):
        if '_id' in kwargs:
            if self.gridfs.exists(kwargs['_id']):
                print('id: {} already exists on gridfs: {}'.format(str(kwargs['_id']), self.gridfs))
                # gridfs.delete(_id)
                return

        self.gridfs.put(file_content, kwargs)
        if not self.gridfs.exists(kwargs['_id']):
            raise Exception('write file to gridfs failed')

    def get_raw(self, meta):
        """ Get raw bin/img from mongo (_id: 'image.raw.hsh')

        :param meta: dict a mongoDB document/meta data
        :return: raw image/bin file content
        """
        try:
            return self.read_file_content_from_gridfs(meta["image"]["raw"]["hash"])
        except KeyError:
            return None

    def get_image_from_gridfs(self, _id, is_uint16=False):
        """ Convert a gridfs file content to image format (numpy array)

        :param _id: gridfs image id
        :param is_uint16: whether it is an uint16 image or not (by default images stored in 8 bits)
        :return: numpy array (image)
        """
        img_data = self.read_file_content_from_gridfs(_id)
        img_data = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_UNCHANGED)
        uint_type = np.uint16 if is_uint16 else np.uint8

        return np.asarray(img_data).astype(uint_type)

    def get_yuv(self, meta, y_level=4):
        """Get y, u, v images from gridfs based on meta data

        :param meta:
        :param y_level:
        :return: y, u, v images (numpy arrays)
        """
        try:
            y = self.get_image_from_gridfs(meta["image"]["y"]["chipsp{}".format(y_level)]["hash"], True)
            u = self.get_image_from_gridfs(meta["image"]["u"]["chipsp{}".format(int(y_level) + 1)]["hash"])
            v = self.get_image_from_gridfs(meta["image"]["v"]["chipsp{}".format(int(y_level) + 1)]["hash"])
        except KeyError:
            return None

        return y, u, v

    def get_ids(self, query=None):
        """ Query id-s in your collection, based on your query, or get all id-s when query not provided

        :param query: dict a valid mongoDB query
        :return: list of dict-s containing {'_id': '{your_id}'}
        """
        query = {} if query is None else query
        result = self.collection.find(query, {"_id": 1})
        return list(result)
