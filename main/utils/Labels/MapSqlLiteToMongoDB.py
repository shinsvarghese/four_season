from .LabelDataAnnotations import Annotations
class Mapper:

    def __init__(self):
        self.dataMappingDictionary = {}
        self.recordingFolder = 'PATH'
        self.recordingName = 'SEQUENCE'
        self.timeStamp = "TIMESTAMP"
        self.recordingDate = 'recording_date'
        self.cameraDayTime = 'camera_daytime'
        self.recordingType = 'recording_type'
        self.labelSource = 'label_source'
        self.__annotationsName = 'annotations'
        self.sensorPlatform = 'SENSOR_PLATFORM'
        self.__annotationI = Annotations()

        self.createMap()

    def createMap(self):
        self.dataMappingDictionary[self.recordingFolder] = 'sourcefolder'
        self.dataMappingDictionary[self.timeStamp] = 'timestamp'
        self.dataMappingDictionary[self.recordingName] = 'sourcefile'


    def performMapping(self, PathData, SignData,ROIandFrameData, MongoMappedData,LabelSource,signType):

        MongoMappedData[self.dataMappingDictionary[self.recordingFolder]] = PathData[self.recordingFolder]
        #MongoMappedData[self.recordingDate] = '?'

        MongoMappedData[self.dataMappingDictionary[self.timeStamp]] = ROIandFrameData[self.timeStamp]
        MongoMappedData[self.dataMappingDictionary[self.recordingName]] = ROIandFrameData[self.recordingName]
        if SignData[self.sensorPlatform]:
            MongoMappedData[self.recordingType] = SignData[self.sensorPlatform]
        else:
            MongoMappedData[self.recordingType] ="unknown"
        MongoMappedData[self.labelSource] = LabelSource['LABEL_CHECKPOINT']


        #perform update of the data
        self.__annotationI.performUpdate(SignData,ROIandFrameData,signType)

        # Annotations of the label
        MongoMappedData[self.__annotationsName] = self.__annotationI.getData()

    def updateData(self, PathData, SignData, ROIandFrameData, MongoMappedData,signType):
        #perform update of the data
        self.__annotationI.performUpdate(SignData,ROIandFrameData,signType)

        #get an updated info
        self.__annotationI.getUpdatedData(MongoMappedData[self.__annotationsName])
