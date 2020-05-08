from .MapperUpdate import MapperInterface
from .DataEnum import DataEnum

class pvsbjectLabel(MapperInterface):

    def __init__(self):
        self.__pvsPartly='PVS_PARTLY'
        self.__pvsColor='PVS_COLOR'
        self.__pvsReversed='PVS_REVERSED'
        self.__roiPartly = 'ROI_PARTLY'
        self.__roiInvisible= 'ROI_INVISIBLE'
        self.__pvsContaminated='PVS_CONTAMINATED'
        self.__signClass = 'SIGN_CLASS'
        self.ObjectLabelData =  [
                                      [self.__pvsPartly, None] \
                                    , [self.__pvsColor, None] \
                                    , [self.__pvsReversed,None] \
                                    , [self.__roiPartly, None] \
                                    , [self.__roiInvisible, None] \
                                    , [self.__pvsContaminated, None] \
                                    , [self.__signClass, None] \

                                ]
        self.__dataMappingDictionary = {}
        self.createMap()

    def createMap(self):
        self.__dataMappingDictionary[self.__signClass] = 'sign_class'
        self.__dataMappingDictionary[self.__pvsPartly] = 'pvs_partly'
        self.__dataMappingDictionary[self.__pvsColor] = 'pvs_color'
        self.__dataMappingDictionary[self.__pvsReversed] = 'pvs_reversed'
        self.__dataMappingDictionary[self.__roiPartly] = 'roi_partly'
        self.__dataMappingDictionary[self.__roiInvisible] = 'roi_invisible'
        self.__dataMappingDictionary[self.__pvsContaminated] = 'contaminated'



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