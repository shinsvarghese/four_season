from .MapperUpdate import MapperInterface
from .DataEnum import DataEnum

class objectLabel(MapperInterface):

    def __init__(self):
        self.__signClass = 'SIGN_CLASS'
        self.__signRelationMain = 'SIGN_RELATION_MAIN'
        self.__signEmbedded = 'SIGN_EMBEDDED'
        self.__signOnMultiSignMounting = 'SIGN_ON_MULTI_SIGN_MOUNTING'
        self.__signContaminated = 'SIGN_CONTAMINATED'
        self.__signTwisted = 'SIGN_TWISTED'
        self.__signDisabled = 'SIGN_DISABLED'
        self.__signFlashing = 'SIGN_FLASHING'
        self.__signInvalid = 'SIGN_INVALID'
        self.__signForAnotherRoad = 'SIGN_FOR_OTHER_ROAD'
        self.__signLaneDistance = 'SIGN_LANE_DISTANCE'
        self.ObjectLabelData =  [
                                      [self.__signClass, 0.0] \
                                    , [self.__signRelationMain, 0.0] \
                                    , [self.__signEmbedded, 0.0] \
                                    , [self.__signOnMultiSignMounting, 0.0] \
                                    , [self.__signContaminated, 0.0] \
                                    , [self.__signTwisted, 0.0] \
                                    , [self.__signDisabled, 0.0] \
                                    , [self.__signFlashing, 0.0] \
                                    , [self.__signInvalid, 0.0] \
                                    , [self.__signForAnotherRoad, 0.0] \
                                    , [self.__signLaneDistance, 0.0]
                                ]
        self.__dataMappingDictionary = {}
        self.createMap()

    def createMap(self):
        self.__dataMappingDictionary[self.__signClass] = 'sign_class'
        self.__dataMappingDictionary[self.__signRelationMain] = 'sign_relation_main'
        self.__dataMappingDictionary[self.__signEmbedded] = 'embedded'
        self.__dataMappingDictionary[self.__signOnMultiSignMounting] = 'on_multi_sign_mounting'
        self.__dataMappingDictionary[self.__signContaminated] = 'contaminated'
        self.__dataMappingDictionary[self.__signTwisted] = 'twisted'
        self.__dataMappingDictionary[self.__signDisabled] = 'disabled'
        self.__dataMappingDictionary[self.__signFlashing] = 'flashing'
        self.__dataMappingDictionary[self.__signInvalid] = 'invalid'
        self.__dataMappingDictionary[self.__signForAnotherRoad] = 'for_other_road'
        self.__dataMappingDictionary[self.__signLaneDistance] = 'lane_distance'


    def performUpdate(self, SignData,ROIandFrameData):
        for ObjectLabeldata in self.ObjectLabelData:
            try:
                ObjectLabeldata[DataEnum.dataValue] = SignData[ObjectLabeldata[DataEnum.dataType]]
            except:
                continue
    def getData(self):
        ObjectLabelDataFinal = {}
        for ObjectLabeldata in self.ObjectLabelData:
            ObjectLabelDataFinal[self.__dataMappingDictionary[ObjectLabeldata[DataEnum.dataType]]] = self.getValueMap(ObjectLabeldata[DataEnum.dataValue])

        return ObjectLabelDataFinal

    def getValueMap(self, dataValue):
        mapData = {}
        mapData['value'] = dataValue
        return mapData