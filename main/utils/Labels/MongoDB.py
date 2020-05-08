try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib import quote_plus

import pymongo
import  ast
import numpy as np
from gridfs import GridFS
from PIL import Image as pil
from io import BytesIO
class MongoDB:

    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.error = None
        self.__isConnected = False
        self.__defaultCollection=None

    def closeConnection(self):
        self.client.close()
    def insert(self,query):
        return self.collection.insert_one(query)
    def find(self,query,filter=None):

        return self.collection.find(query,filter)

    def getList(self):
        return self.collection.find({"_id":'LookUp'})

    def EditFields(self,val,sign,newVal):
       self.collection.find()
       field= 'data.'+str(val)
       self.collection.find_one_and_update({'_id': sign}, { '$set': {field : str(newVal)}},{'upsert':True})# seting fields

    def ShapelistGrouped(self,selectedAttribs):

        andData = "{\"$and\":["
        for data in selectedAttribs:
            if selectedAttribs[data]:
                orData = "{\"$or\":["
                for i in selectedAttribs[data]:
                     attrib="{\"data."+data+ "\": \""+ i+"\"}"
                     orData=orData+attrib+","
                orData=orData.rstrip(',')+"]}"
                andData=andData+orData+","
        andData=andData.rstrip(',')+"]}"
        a=ast.literal_eval(andData)
        return self.collection.find(a)

    def Shapelist(self):
        return self.collection.find({})
    def getGridFs(self):
        return GridFS(self.db, 'image_data')

    def getImage(self, SignSelected=None,hashkey=None):
        ImageData=[]
        if SignSelected:
            check=self.collection.find_one({'_id':SignSelected})
            hash= check['imageData']['fileId']
            self.fs = GridFS(self.db, 'SignDescription_image_data')
            ImageData = np.asarray(pil.open(BytesIO(self.fs.get(hash).read()))).astype(np.uint32)
        if hashkey:
            self.fs = GridFS(self.db, 'image_data')
            ImageData =np.asarray(pil.open(BytesIO(self.fs.get(hashkey).read()))).astype(np.uint32)
            # np.asarray(pil.open(BytesIO(self.fs.get(gridfs_id).read()))).astype(dtype)
        return ImageData
    def updateOne(self,query,up):
        self.collection.update_one(query,up)

    def bplFetch(self,sourcefile,f,cntry):


        check= self.collection.aggregate([{'$match': {'sourcefolder': sourcefile,
                                                      'annotations.framelabel.country.value': cntry,
                                                      'timestamp': {'$gt': 1}}}, {
                                              '$group': {'_id': '$annotations.boxlabel.signId',
                                                         'timeSum':{'$sum':1},
                                                         'Timestamp_Starts': {'$min': '$timestamp'},
                                                         'Timestamp_Ends': {'$max': '$timestamp'}}},
                                          {'$sort': {'Timestamp_Starts': 1}}])


        f.write("  <BatchEntry fileName=")
        f.write("\"")
        f.write(sourcefile)
        f.write("\"")
        f.write(">")
        f.write("\n")
        f.write("    <SectionList>\n")
        for ro in check:

            print (ro["Timestamp_Starts"])
            if ro["Timestamp_Starts"] > ro['Timestamp_Ends']:
                print (ro['_id'])
            else:
                print (ro['_id'])

            print ("next \n")
            f.write("      <Section startTime= ")
            f.write("\"")
            f.write(str(ro['Timestamp_Starts']))
            f.write("\"")
            f.write("  endTime = ")
            f.write("\"")
            f.write(str(ro['Timestamp_Ends']))
            f.write("\"")
            f.write("/>\n")
            f.write("<!-- {}".format(str(ro['timeSum'])))
        f.write("    </SectionList>\n")
        f.write("  </BatchEntry>\n")


    def bpl(self,SelectedCountryList,path):

        cntry_check=self.collection.distinct("annotations.framelabel.country.value")
        cntry_list= list(cntry_check)
        print (cntry_list)

        #print d
        path=str(path)
        path=path+"\\bpl.bpl"
        f=open(path,'w+')
        f.write("<?xml version=" + "\""+ "1.0" + "\""+" encoding= " + "\""+ "UTF-8" +"\""+ "standalone=" + "\""+ "yes"+ "\""+"?>\n")
        f.write("<BatchList>\n")
        for cntry in SelectedCountryList:
            check=self.collection.distinct("sourcefolder",{"annotations.framelabel.country.value":cntry})
            d= list(check)
            if cntry in cntry_list:
              for doc in d:
                   self.bplFetch(str(doc),f,cntry)
        f.write("</BatchList>\n")


    def connectToServer(self, mongoDbUri):
        retVal = True
        try:
            self.client = pymongo.MongoClient(mongoDbUri)
        except pymongo.errors.ConnectionFailure as err:
            self.error = "No Mongo DB Servers Found"
            retVal = False
        finally:
            return retVal
    def connectToDataBase(self, DataBaseName):
        retVal = True
        dbNames = self.client.database_names()
        if DataBaseName in dbNames:
            # Connect to DataBase
            self.db = self.client[DataBaseName]
        else:
            self.error = "Data Base Name Does Not Exist"
            retVal = False
        return retVal

    def GetSignList(self):
        check=self.collection.find_one({"_id":"LatestSignList"})
        return check
		
    def CountryList(self):
        check=self.collection.find_one({"_id":"LatestCountryList"})
        return  check

    def connectToCollection(self, CollectionName):
        retVal = True
        self.__defaultCollection=CollectionName
        collectionNames = self.db.collection_names()
        if CollectionName in collectionNames:
            # Connect to DataBase
            self.collection = self.db[CollectionName]
        else:
            self.error = "Collection Name Does Not Exist"
            retVal = False
        return retVal


    def ConnectToMongo(self, mongoDBUri, DataBaseName, CollectionName):
        if not self.connectToServer(mongoDBUri):
            return False

        if not self.connectToDataBase(DataBaseName):
            return False

        if not self.connectToCollection(CollectionName):
            pass
            # return False

        self.__isConnected = True
        return self.__isConnected

    def updateCollection(self, CollectionName):
        self.__isConnected = self.connectToCollection(CollectionName)
        return self.__isConnected
    def CopyPathInfoToDataBase(self,Data):
        pathCollection= self.db["PathInfo"]
        pathCollection.insert_one(Data)
    def isPathDataEntryExisting(self, SerarchAttribute, SearchVal):
        pathCollection= self.db["PathInfo"]
        return pathCollection.find_one({SerarchAttribute: SearchVal})
    def deleteExistingPathDataEntry(self, SerarchAttribute, SearchVal):
        pathCollection= self.db["PathInfo"]
        return pathCollection.remove({SerarchAttribute: SearchVal})

    def CopyDataToMongoDataBase(self, Data):
        try:
            self.collection.insert(Data)
        except:
            if type(Data) == list:
                [self.collection.save(doc) for doc in Data]
            else:

                self.collection.save(Data)


    def updateCollection(self,CollectionName):
        self.collection=self.db[CollectionName]
    def getDefaultCollection(self):
        return self.__defaultCollection


    def isEntryExisting(self, SerarchAttribute, SearchVal):
        return self.collection.find_one({SerarchAttribute: str(SearchVal)})

    def deleteExistingEntry(self, SerarchAttribute, SearchVal):
        return self.collection.remove({SerarchAttribute: SearchVal})

    def isConnected(self):
        return self.__isConnected

    def getConnection(self, collectionName):
        connection = None
        if collectionName in  self.db.collection_names():
            connection = self.db[collectionName]

        return connection

    def __del__(self):
        if self.client is not None:
            self.client.close()

    def getDoc(self, timestamp, rec):
        return self.col.find_one({'timestamp': int(timestamp), 'sourcefile': rec})

    def insertDoc(self, data):
        try:
            self.local_col.insert(data)

        except:
            print("Duplicate")
            # self.col.update({'_id':data['_id']},data)

    def insertImage(self, img, hash, file,contentType="rggb"):

        if not self.gfs.exists(_id=hash):
            with self.gfs.new_file(_id=hash, filename=file, contentType=contentType) as f_db:
                f_db.write(img)
            print("insert", file)
        else:
            print ("file Exists!!")