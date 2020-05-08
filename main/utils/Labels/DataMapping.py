from .SqlLite import SqlLite
from .MongoDB import MongoDB
from .SqlStringHelper import SqlStringHelper
from .MapSqlLiteToMongoDB import Mapper
from .UserAndTime import UserAndTimeInfo
import os
import logging
import threading
from .shapeShifter import  ShapeFix
class DataBaseDataMapper:

    def __init__(self):
        self.defaultDB=None
        self.defaultCollection=None
        self.mappedSequence = 'LatestMappedSequenceList'
        self.signDiscription = 'SignDescription'
        self.SignList ='LatestSignList'
        self.CountryList='LatestCountryList'
        self.SequenceList = 'LatestSequenceList'
        self.SensorList = 'LatestSensorList'
        self.logFileName = 'LabelConverter.log'
        self.uri = None
        self.shapeI=ShapeFix()
        self.MongoDbI = MongoDB()
        self.MongoDbISignDesc= MongoDB()
        self.__isMongoDBConnected = False
        self.SqlStringHelperI = SqlStringHelper()
        self.SqlLiteI = None
        self.MapperI = Mapper()
        self.__pathinfoCollection="PathInfo"

        # update for logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # delete the file if it already exists
        try:
            os.remove(self.logFileName)
        except OSError:
            pass
        # create a file handler
        self.handler = logging.FileHandler(self.logFileName)
        self.handler.setLevel(logging.INFO)

        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(self.handler)
        self.logger.addHandler(self.handler)

        self.__isThreadingActive = False


    def find(self, query):
        import json
        query = json.loads(str(query))
        return  self.MongoDbI.find(query)

    def getSignType(self,signType):
        self.signType=signType

    def getImage(self,SignSelected,hashKey):
        if SignSelected:
            self.MongoDbISignDesc.updateCollection(self.signDiscription)
            ImageData=  self.MongoDbISignDesc.getImage(SignSelected,None)
        if hashKey:
            ImageData=self.MongoDbI.getImage(None,hashKey)
        self.MongoDbI.updateCollection(self.MongoDbI.getDefaultCollection())
        return ImageData

    def bpl(self,SelectedCountryList,path):
        self.MongoDbI.bpl(SelectedCountryList,path)

    def ShapelistGrouped(self,selectedAttribs):
        self.MongoDbISignDesc.updateCollection(self.signDiscription)
        ShapeList = self.MongoDbISignDesc.ShapelistGrouped(selectedAttribs)
        #self.MongoDbI.updateCollection(self.MongoDbI.getDefaultCollection())
        return ShapeList

    def Shapelist(self):
        self.MongoDbISignDesc.updateCollection(self.signDiscription)
        shapeList=self.MongoDbISignDesc.Shapelist()
        #self.MongoDbI.updateCollection(self.MongoDbI.getDefaultCollection())

        return shapeList

    def EditFields(self,val,Sign,newVal):
        self.MongoDbISignDesc.updateCollection(self.signDiscription)
        self.MongoDbISignDesc.EditFields(val,Sign,newVal)
        #self.MongoDbI.updateCollection(self.MongoDbI.getDefaultCollection())

    def getList(self):
        self.MongoDbISignDesc.updateCollection(self.signDiscription)
        attributeList = self.MongoDbISignDesc.getList()
       # self.MongoDbISignDesc.updateCollection(self.MongoDbI.getDefaultCollection())
        return attributeList

    def performMongoDBConnection(self, uri, dataBaseName, collectionName):
        self.defaultDB = dataBaseName
        self.defaultCollection = collectionName
        self.uri = uri
        self.__isMongoDBConnected = self.MongoDbI.ConnectToMongo(uri, dataBaseName, collectionName) and self.MongoDbISignDesc.ConnectToMongo(uri, dataBaseName, collectionName)

        return self.__isMongoDBConnected

    def isNotArchived(self,filePath):
            isNotArchived = True
            if os.path.isfile(filePath):
                size=os.path.getsize(filePath)
                if size < 10000:
                    isNotArchived=False
            else:
                isNotArchived=False
            # self.MongoDbI.updateCollection(self.__pathinfoCollection)
            # fileInfo=self.MongoDbI.isEntryExisting("_id",filePath)
            # if fileInfo:
            #     if fileInfo["status"] == "Archived":
            #         isNotArchived=False
            #     elif fileInfo["status"]== "not found":
            #         isNotArchived=False
            # else:
            #     self.logger.info( "no info present for %s in collection ",filePath)
            #
            # defaultCollection = self.MongoDbI.getDefaultCollection()
            # self.MongoDbI.updateCollection(defaultCollection)
            return isNotArchived


    def isMongoDBConnected(self):
        return self.__isMongoDBConnected

    def getMongoDBConnectionError(self):
        return self.MongoDbI.error

    def GetSignList(self):
         self.MongoDbISignDesc.updateCollection(self.SignList)
         cursor = self.MongoDbISignDesc.GetSignList()
     #    self.MongoDbI.updateCollection(self.MongoDbI.getDefaultCollection())
         return cursor
		 
    def GetCountryList(self):
        self.MongoDbISignDesc.updateCollection(self.CountryList)
        cursor=self.MongoDbISignDesc.CountryList()

        # self.MongoDbI.updateCollection(self.MongoDbI.getDefaultCollection())
        return cursor

    def updateCountryData(self, CountryData):
        CountryList = []
        self.MongoDbI.updateCollection(self.CountryList)
        id = ('LatestCountryList')
        for EachCountryData in CountryData:
            if EachCountryData["COUNTRY"]:
                CountryList.append(EachCountryData["COUNTRY"])
        CountryDataList = self.MongoDbI.isEntryExisting('_id', id)
        if CountryDataList:
            self.MongoDbI.deleteExistingEntry('_id', id)

        CountryDataList = {'_id': id}
        CountryDataList['Country List'] = CountryList
        self.MongoDbI.CopyDataToMongoDataBase(CountryDataList)
        self.MongoDbI.updateCollection(self.MongoDbI.getDefaultCollection())

    def mapCountryData(self, sqlLitePath):
        self.SqlLiteI = SqlLite(str(sqlLitePath))
        self.logger.info( "Extracting Country Data................")
        CountryData = self.SqlLiteI.ExtractData(self.SqlStringHelperI.getCountryListString(self.signType))
        self.logger.info( "Extracted Country Data................")
        self.updateCountryData(CountryData)

    def updateSignClassData(self, SignClassData):
        SignList = []
        self.MongoDbI.updateCollection(self.SignList)
        id = ('LatestSignList')
        for EachSignClassData in SignClassData:
            if EachSignClassData["SIGN_CLASS"]:
                SignList.append(EachSignClassData["SIGN_CLASS"])
        SignDataList = self.MongoDbI.isEntryExisting('_id', id)
        if SignDataList:
            self.MongoDbI.deleteExistingEntry('_id', id)

        SignDataList = {}
        SignDataList['_id'] = id
        SignDataList['Sign List'] = SignList
        self.MongoDbI.CopyDataToMongoDataBase(SignDataList)
        self.MongoDbI.updateCollection(self.MongoDbI.getDefaultCollection())

    def mapSignClassData(self, sqlLitePath):
        self.SqlLiteI = SqlLite(str(sqlLitePath))
        self.logger.info( "Extracting Sign Class Data................")
        SignClassData = self.SqlLiteI.ExtractData(self.SqlStringHelperI.getSignListString(self.signType))
        self.logger.info( "Extracted Sign Class Data................")
        self.updateSignClassData(SignClassData)

    def updateSequenceListToMongoDB(self, LatestSequenceList):
        self.logger.debug( LatestSequenceList)
        self.MongoDbI.updateCollection(self.SequenceList)
        id = ('LatestSequenceList')
        if LatestSequenceList:
            LatestSequenceListMongoDBData = self.MongoDbI.isEntryExisting('_id', id)
            if LatestSequenceListMongoDBData :
                self.MongoDbI.deleteExistingEntry('_id', id)

            LatestSequenceListMongoDBData = LatestSequenceList
            LatestSequenceListMongoDBData['_id'] = id


            self.MongoDbI.CopyDataToMongoDataBase(LatestSequenceListMongoDBData)
            self.MongoDbI.updateCollection(self.MongoDbI.getDefaultCollection())

    def updateSequenceList(self, sqlLitePath):
        self.SqlLiteI = SqlLite(sqlLitePath)
        self.MongoDbI.updateCollection(self.CountryList)
        id = ('LatestCountryList')

        CountryListData = self.MongoDbI.isEntryExisting('_id', id)
        LatestSequenceList = {}
        if CountryListData:
            CountryList = CountryListData['Country List']
            for country in CountryList:
                # fetch the SqlData
                self.logger.info( "Extracting %s Data.............", str(country))
                sqlCountryData = self.SqlLiteI.ExtractData(self.SqlStringHelperI.getSequenceList(country,self.signType))
                self.logger.info( "Done Extracting %s  Data........", str(country))
                # Create a sequence List from country
                sequenceList = []
                while(True):
                    Data = sqlCountryData.fetchone()

                    if not Data:
                        break

                    sequenceList.append(Data['SEQUENCE'])

                LatestSequenceList[country] = sequenceList
        self.updateSequenceListToMongoDB(LatestSequenceList)
        self.MongoDbI.updateCollection(self.MongoDbI.getDefaultCollection())

    def updateSensorData(self, SensorData):
        self.MongoDbI.updateCollection(self.SensorList)
        id = ('LatestSensorList')
        sensorList = []
        for EachSensor in SensorData :
            sensorList.append(EachSensor['SENSOR_PLATFORM'])

        SensorListData = self.MongoDbI.isEntryExisting('_id', id)


        if SensorListData:
            self.MongoDbI.deleteExistingEntry('_id', id)

        SensorListData = {}
        SensorListData['_id'] =  id
        SensorListData['SensorList'] = sensorList
        self.MongoDbI.CopyDataToMongoDataBase(SensorListData)
        self.MongoDbI.updateCollection(self.MongoDbI.getDefaultCollection())

    def updateSensorList(self,sqlLitePath):
        self.SqlLiteI = SqlLite(str(sqlLitePath))
        self.logger.info( "Extracting Sensor Data................")
        SensorData = self.SqlLiteI.ExtractData(self.SqlStringHelperI.getSensorListString())
        self.logger.info( "Extracted Sensor Data................")
        self.updateSensorData(SensorData)

    def getInitialSignListData(self, totalsignList):
        signList = {}
        for sign in totalsignList:
            signList[self.modifyKey(sign)] = []
        return signList
    def getOriginalKey(self,key):
        try:
            return key.replace("{_}",".")
        except:
            print (key)
    def modifyKey(self, key):
        try:
            return key.replace(".", "{_}")
        except:
            print (key)

    def getOriginalKey(self, modifiedKey):
        return modifiedKey.replace("{_}", ".")

    def mappedSequenceData(self, sqlLitePath):
        self.SqlLiteI = SqlLite(str(sqlLitePath))
        self.MongoDbI.updateCollection(self.CountryList)
        countryList = self.MongoDbI.isEntryExisting('_id', self.CountryList)
        self.MongoDbI.updateCollection(self.SignList)
        signList = self.MongoDbI.isEntryExisting('_id', "LatestSignList")
        self.MongoDbI.updateCollection(self.SequenceList)
        sequenceList = self.MongoDbI.isEntryExisting('_id', self.SequenceList)

#        tempFlag=0
        if countryList and signList and sequenceList:


            totalCountryList = countryList['Country List']
            totalSignList = signList['Sign List']
            self.MongoDbI.updateCollection(self.mappedSequence)
            mappedSequenceData = self.MongoDbI.isEntryExisting('_id', self.mappedSequence)

            if mappedSequenceData:
                self.MongoDbI.deleteExistingEntry('_id', self.mappedSequence)
            mappedSequenceData = {}
            for country in totalCountryList:
 ##                  if country != "EE":
   #                     continue
    #                else:
     #                   tempFlag=1
                self.logger.info( "%s in progress.........",str(country) )
                countrySequenceList = sequenceList[country]
                signList = self.getInitialSignListData(totalSignList)
                for eachCountrySequence in countrySequenceList:
                    extractedData = self.SqlLiteI.ExtractData(
                        self.SqlStringHelperI.getCheckSequenceString(eachCountrySequence,self.signType))

                    while (True):
                        signClassDataExtracted = extractedData.fetchone()

                        if not signClassDataExtracted:
                            break
                        if signClassDataExtracted['SIGN_CLASS']==None:
                            continue

                        modifiedKey = self.modifyKey(signClassDataExtracted['SIGN_CLASS'])
                        countrySeqList = signList[modifiedKey]
                        countrySeqList.append(eachCountrySequence)
                        signList[modifiedKey] = countrySeqList
                mappedSequenceData['_id'] = country
                mappedSequenceData['sequenceList'] = signList
                self.logger.info( "%s Done.........",str(country), )
           # mappedSequenceData['_id'] = self.mappedSequence
                self.MongoDbI.CopyDataToMongoDataBase(mappedSequenceData)

        self.MongoDbI.updateCollection(self.MongoDbI.getDefaultCollection())
#        self.displayMessage("The Lookup tables have been updated")

    def createSignIDList(self, SignData):
        SignIDList = []
        for eachSignData in SignData:
            SignIDList.append(eachSignData['SIGN_ID'])
        return SignIDList

    def isPathArchived(self,sequenceList):
        for sequence in sequenceList:
            PathData = self.SqlLiteI.ExtractData(self.SqlStringHelperI.getPathString(sequence,self.signType)).fetchone()
            filePath = PathData["PATH"]

            PathInfo=self.MongoDbI.isPathDataEntryExisting("_id",filePath)
            isDataExisting=True
            if (not PathInfo):
                PathInfo={}
                PathInfo["_id"] = filePath
                isDataExisting=False
            fileExistance = "Present"
            try:
                if os.path.getsize(filePath)<2040:
                    fileExistance ="Archived"
            except Exception as err:
                fileExistance= "not found"
            PathInfo["status"] = fileExistance
            self.logger.debug(filePath, fileExistance)
        if isDataExisting:
            self.MongoDbI.deleteExistingPathDataEntry("_id",filePath)
        self.MongoDbI.CopyPathInfoToDataBase(PathInfo)


    def reEstablishConnection(self):
       self.MongoDbI.closeConnection()
       self.performMongoDBConnection(self.uri
                                     ,self.defaultDB
                                     ,self.defaultCollection
                                     )

    def extractForSequence(self, country, signType, sequence):
        #count = 0
        self.logger.info("Extracting Path Data.....")
        PathData = self.SqlLiteI.ExtractData(self.SqlStringHelperI.getPathString(sequence,self.signType)).fetchone()
        # perform operations only if the recording is not archived
        # if self.isNotArchived(PathData["PATH"]):

        signType=self.getOriginalKey(signType)
        self.logger.info("Extracting Sign Data from sqlite..... for %s    %s    %s", sequence, country, signType)
        SignIDData = self.SqlLiteI.ExtractData(self.SqlStringHelperI.getSignIDString(sequence, signType,self.signType))
        self.logger.info("Done Extracting Sqlite Data!!")
        self.logger.info("Extracting ROI and Frame Data.....")
        ROIandFrameData = self.SqlLiteI.ExtractData(
            self.SqlStringHelperI.getROIAndFrameInfoString(sequence, self.createSignIDList(SignIDData), country,self.signType))
        self.logger.info("Done Extracting ROI and Frame Data!!")
        # self.logger.info("Done Extracting All Data!!")
        LabelSource = self.SqlLiteI.ExtractData(self.SqlStringHelperI.getLabelSource(self.signType)).fetchone()
        MappedDataList = []
        for eachROIandFrameData in ROIandFrameData:
            if eachROIandFrameData['ROI_Y1'] == eachROIandFrameData['ROI_Y2']:
                continue
            # check if the document exists already
            signId = eachROIandFrameData["SIGN_ID"]
            cur_id = (eachROIandFrameData["SEQUENCE"][:-4].lower() + "-" + str(eachROIandFrameData["TIMESTAMP"]) + ".xml")
            MappedData = self.MongoDbI.isEntryExisting('_id', cur_id)
            SignData = self.SqlLiteI.ExtractData(
                self.SqlStringHelperI.getSignDataString(sequence, signType, signId,self.signType)).fetchone()
            isDataExisting = True

            if (not MappedData):
                MappedData = {}
                MappedData['_id'] = cur_id
                isDataExisting = False
                for TempMappeddata in MappedDataList:
                    if cur_id == TempMappeddata['_id']:
                        MappedData = TempMappeddata
                        MappedDataList.remove(TempMappeddata)
                        isDataExisting = True
                        break

            UserAndTimeInfoI = UserAndTimeInfo()
            UserAndTimeInfoI.updateLabelCreationInfo(MappedData, True)
            # call to mapping
            DuplicateBoxlabel = False
            if isDataExisting:
                for x in MappedData["annotations"]["boxlabel"]:
                    if x["signId"] == signId:
                        MappedData["annotations"]["boxlabel"].remove(x)
                        DuplicateBoxlabel = True
                #         break
                # if DuplicateBoxlabel == False:
                self.MapperI.updateData(PathData, SignData, eachROIandFrameData, MappedData,self.signType)
            else:
                self.MapperI.performMapping(PathData, SignData, eachROIandFrameData, MappedData, LabelSource,self.signType)

            if DuplicateBoxlabel:
                self.logger.info("Existing Box Label, overwriting to mongoDb")
                # continue
            if isDataExisting:
                # self.logger.info("Data existing , Deleting  the fields")
                # self.MongoDbI.deleteExistingEntry('_id', cur_id)
                pass

            if MappedData:
                # self.logger.info((len(MappedDataList), '- Mapping completed'))
                MappedData = self.shapeI.fixShape(MappedData)


                self.CopyDataToMongoDataBase(MappedData)

    def CopyDataToMongoDataBase(self, MappedDataList):
        if(len(MappedDataList) > 0):
            self.reEstablishConnection()
            if(self.__isThreadingActive):
                thread = threading.Thread(target=self.MongoDbI.CopyDataToMongoDataBase, args=(MappedDataList,))
                thread.start()
            else:
                self.MongoDbI.CopyDataToMongoDataBase(MappedDataList)

    def extractAllData(self, country, signType, sequenceList):
        #update frame infofilePath
        modifiedSequence=[]

        for sequence in sequenceList:
            sensorType=self.SqlLiteI.ExtractData(
                self.SqlStringHelperI.getSensorType(str(sequence))).fetchone()

            # if sensorType['SENSOR_PLATFORM']=="MFC_4xx" or sensorType['SENSOR_PLATFORM']=="MFC_3xx":
            if "MFC" in sensorType['SENSOR_PLATFORM']:
                # count=count+1
                modifiedSequence.append(sequence)
            else:
                pass


        if len(modifiedSequence) != 0:
            for sequence in modifiedSequence:
                self.extractForSequence(country, signType, sequence)

    def extractLabels(self, sqlLitePath, countryList, signTypeList):
        retVal = False
        self.SqlLiteI = SqlLite(sqlLitePath)
        # get recording Data specific to country and sign type from Mongo DB
        for country in countryList:

            self.MongoDbI.updateCollection(self.mappedSequence)
            MappedSequenceList = self.MongoDbI.isEntryExisting('_id',country)
            self.MongoDbI.updateCollection(self.MongoDbI.getDefaultCollection())
            try:
                if MappedSequenceList:
                        retVal = True

                        signListData = MappedSequenceList["sequenceList"]
                        for signType in signTypeList:
                            signType=str(signType)

                            signType= self.modifyKey( signType)

                            sequenceList = signListData[signType]

                            self.extractAllData(country, signType, sequenceList)
            except Exception as e:
                print(e)

        self.logger.info("Done Extracting All data!!!")
        self.MongoDbI.closeConnection()

        return retVal
