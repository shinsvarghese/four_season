import pymongo
import numpy as np
from gridfs import GridFS
from PIL import Image as pil
from io import BytesIO
import scipy.misc
import pickle

class MongoDB:
    # def __init__(self,uri="ozd0127u:27018",db="Labels",coll_source="Shape_Latest_7_Classes",coll_dest="Latest_Modified"):
    def __init__(self,uri="mongodb://LabellingTeam:Labelling@ozd2106u:27018/Labels",db="Labels",coll_source="Shape_Latest_7_Classes",coll_dest="Latest_Modified"):
        self.client=pymongo.MongoClient(uri)
        self.db=self.client[db]
        self.collection=self.db[coll_source]
        self.collDest=self.db[coll_dest]

    def getImage(self,  hashkey):

        if hashkey:
            self.fs = GridFS(self.db, 'image_data')
            ImageData = np.asarray(pil.open(BytesIO(self.fs.get(hashkey).read()))).astype(np.uint32)
            # np.asarray(pil.open(BytesIO(self.fs.get(gridfs_id).read()))).astype(dtype)
        return ImageData

    def getData(self,query):
        return self.collection.find(query).sort('timestamp',1)

    def getSingleData(self,query):
        return self.collDest.find(query)

    def update(self,doc):
        # print(doc)
        # self.collection.update({'_id':doc['_id']},doc)
        self.collDest.save(doc)