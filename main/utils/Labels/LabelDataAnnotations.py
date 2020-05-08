__author__ = 'uidq1602'
from .MapperUpdate import MapperInterface
from .frameLabelData import frameLabel
from .RoiData import Roi
class Annotations(MapperInterface):

    def __init__(self):
        self.__boxLabelName = 'boxlabel'
        self.__annotationCompleted = 'anno_completed'
        self.__frameLabel = 'framelabel'
        self.__annotationFlag = 'Rectangle_Signs'
        self.__frameDataI = frameLabel()
        self.__roi=Roi()

    def performUpdate(self,SignData,ROIandFrameData,signType):
        self.__roi.performUpdate(SignData,ROIandFrameData,signType)
        self.__frameDataI.performUpdate(SignData,ROIandFrameData)

    def getData(self):
        annotationsData = {}
        # Add box label data below

        annotationsData[self.__boxLabelName]=self.__roi.getData()

        # Add Annotations completed data below
        #annotationsData[self.__annotationCompleted] = self.getAnnotationFlag()

        # Add frame label data below

        annotationsData[self.__frameLabel] = self.__frameDataI.getData()
        return  annotationsData


    def getAnnotationFlag(self):
        annotationFlag = {}
        annotationFlag[self.__annotationFlag] = True
        return annotationFlag

    def getUpdatedData(self, annotationsData):

        annotationsData[self.__boxLabelName]=self.__roi.getUpdatedData(annotationsData[self.__boxLabelName])
