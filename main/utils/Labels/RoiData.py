from .MapperUpdate import MapperInterface
from .DataEnum import DataEnum
from .objectLabelData import objectLabel
from  .pvsAttribs import pvsbjectLabel
class Roi(MapperInterface):
    def __init__(self):
        self.__RoiX1 = 'ROI_X1'
        self.__RoiX2 = 'ROI_X2'
        self.__RoiY1 = 'ROI_Y1'
        self.__RoiY2 = 'ROI_Y2'
        self.__signId = 'SIGN_ID'
        self.RoiList={}
        self.RoiData =  [
                              [self.__RoiX1, 0] \
                            , [self.__RoiX2, 0] \
                            , [self.__RoiY1, 0] \
                            , [self.__RoiY2, 0] \
                        ]

        self.SignData = [
                            [self.__signId, 0]
        ]
        self.__height = 'height'
        self.__width = 'width'
        self.__aspectRatio = 'aspectratio'
        self.__class = 'class'
        self.__className = 'Rectangle_Signs'
        self.__area = 'area'
        self.__attributes = 'attributes'
        self.__dataMappingDictionary = {}
        self.createMap()
        self.__objectLabelI = objectLabel()
        self.__pvsbjectLabelI=pvsbjectLabel()

    def createMap(self):
        self.__dataMappingDictionary[self.__RoiX1] = 'x0'
        self.__dataMappingDictionary[self.__RoiY1] = 'y0'
        self.__dataMappingDictionary[self.__RoiX2] = 'x1'
        self.__dataMappingDictionary[self.__RoiY2] = 'y1'
        self.__dataMappingDictionary[self.__signId] = 'signId'


    def performUpdate(self, SignData , ROIandFrameData,signType):
        self.signType=signType
        for RoiData in self.RoiData:
            RoiData[DataEnum.dataValue] = ROIandFrameData[RoiData[DataEnum.dataType]]
            self.RoiList[RoiData[DataEnum.dataType]]=RoiData[DataEnum.dataValue]


        for signData in self.SignData:
            signData[DataEnum.dataValue] = SignData[signData[DataEnum.dataType]]
        if  self.signType=='mainSign':
            self.__objectLabelI.performUpdate(SignData , ROIandFrameData)
        if  self.signType=='PVS':
            self.__pvsbjectLabelI.performUpdate(SignData,ROIandFrameData)
    def updateData(self):
        ROIDataFinal = {}
        for RoiData in self.RoiData:
            ROIDataFinal[self.__dataMappingDictionary[RoiData[DataEnum.dataType]]] = RoiData[DataEnum.dataValue]

        for signData in self.SignData:
            ROIDataFinal[self.__dataMappingDictionary[signData[DataEnum.dataType]]] = signData[DataEnum.dataValue]


        height = self.RoiList[self.__RoiY2] - self.RoiList[self.__RoiY1]
        ROIDataFinal[self.__height] = height
        width = self.RoiList[self.__RoiX2] - self.RoiList[self.__RoiX1]
        ROIDataFinal[self.__width] = width
        aspectRatio=0.00
        aspectRatio=float(width)/float(height) ## externally doing type conversation
        ROIDataFinal[self.__aspectRatio] = aspectRatio
        ROIDataFinal[self.__class] = self.__className


        ROIDataFinal[self.__area] = float(width) * float(height) ## externally doing type conversation
        if self.signType == 'PVS':
            ROIDataFinal[self.__attributes]=self.__pvsbjectLabelI.getData()
        if self.signType=='mainSign':
            ROIDataFinal[self.__attributes] = self.__objectLabelI.getData()

        return ROIDataFinal

    def getData(self):
        ROIDataList = []
        ROIDataList.append(self.updateData())
        return ROIDataList


    def getUpdatedData(self, ROIDataList):
        ROIDataList.append(self.updateData())
        return ROIDataList
