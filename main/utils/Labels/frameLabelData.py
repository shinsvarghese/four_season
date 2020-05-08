from .MapperUpdate import MapperInterface
from .DataEnum import DataEnum

class frameLabel(MapperInterface):

    def __init__(self):
        self.__roadType = 'ROAD_TYPE'
        self.__weather = 'WEATHER'
        self.__lightConditions = 'LIGHT_CONDITIONS'
        self.__streetConditions = 'STREET_CONDITIONS'
        self.__country = 'COUNTRY'
        self.__tunnel = 'TUNNEL'
        self.__roadWorks = 'ROAD_WORKS'
        self.__contamination = 'CONTAMINATION'
        self.__paving       = 'PVS_PAVING'
        self.__frameLabelData =   [
                                      [self.__roadType, ''] \
                                    , [self.__weather, ''] \
                                    , [self.__lightConditions, ''] \
                                    , [self.__streetConditions, ''] \
                                    , [self.__country, ''] \
                                    , [self.__tunnel, ''] \
                                    , [self.__roadWorks, ''] \
                                    , [self.__contamination, ''] \
                                    # , [self.__paving,''  ]
                                ]

        self.__dataMappingDictionary = {}
        self.createMap()

    def createMap(self):
        self.__dataMappingDictionary[self.__roadType] = 'roadType'
        self.__dataMappingDictionary[self.__weather] = 'weather'
        self.__dataMappingDictionary[self.__lightConditions] = 'light_conditions'
        self.__dataMappingDictionary[self.__streetConditions] = 'street_conditions'
        self.__dataMappingDictionary[self.__country] = 'country'
        self.__dataMappingDictionary[self.__tunnel] = 'tunnel'
        self.__dataMappingDictionary[self.__roadWorks] = 'road_works'
        self.__dataMappingDictionary[self.__contamination] = 'contamination'
        self.__dataMappingDictionary[self.__paving]        =   'paving'

    def performUpdate(self, SignData,ROIandFrameData):
        for frameLabelData in self.__frameLabelData:
            try:
                frameLabelData[DataEnum.dataValue] = ROIandFrameData[frameLabelData[DataEnum.dataType]]
            except:
                continue
    def getData(self):
        FrameLabelDataFinal = {}
        #for frameLabelData in self.frameLabelData: # Before it written like this
        for frameLabelData in self.__frameLabelData:
            FrameLabelDataFinal[self.__dataMappingDictionary[frameLabelData[DataEnum.dataType]]] = self.getValueMap(frameLabelData[DataEnum.dataValue])
        return FrameLabelDataFinal

    def getValueMap(self, dataValue):
        mapData = {}
        mapData['value'] = dataValue
        return mapData
