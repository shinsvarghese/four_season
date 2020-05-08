#
"""
Created on 21 Apr 2019 01:50

@projectname: FourSeasons
@filename: fs_four_seasons
@description: 
@comments: 
@author: Senthil
"""

from utils.fs_data_analysis import DataAnalysis
from PyQt5 import QtWidgets
from ui.fs_main_window import Ui_MainWindow
#from fs_dms_to_mongodb import UiDMStoMongoDB
from utils.fs_defines import UiShape
from utils.fs_annotation import  UiAnnotations
import sys
# sys.path.insert(0, 'Labels/')
from  utils.Labels.LabelConverter import StartQT4
from utils.fs_get_raw_data import UIRawData
from PyQt5 import QtCore, QtGui



class UiFourSeasons(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):

        super(UiFourSeasons, self).__init__()
        self.ui_shape = []
        self.setupUi(self)
        self.update_shape(UiShape.medium)

        # additional page ui objects
        # self.ui_dms_to_mongodb = UiDMStoMongoDB(self)
        self.actionDMS_to_MongoDB.triggered.connect(self.sqlToMongo)
        self.data_analysis.triggered.connect(self.abc)
        # data analysis page
        self.data=DataAnalysis(self)
        #Annotations correction page
        self.anno=UiAnnotations(self)
        self.actionAnnotations.triggered.connect(self.setAnnotationPage)
        self.actionSQL_to_MongoDB.triggered.connect(self.SqlToMongo)
        self.ui_sql_to_mongo=StartQT4(self)
        # self.raw=UIRawData(self)
        self.actionImage_Dump.triggered.connect(self.rawData)
        self.init_setup(0)

        self.showMaximized()
    def sqlToMongo(self):
        self.init_setup(0)
    def setAnnotationPage(self):
        self.init_setup(3)
        self.update_shape(UiShape.big)

    def SqlToMongo(self):
        self.init_setup(4)
        self.update_shape((1300,860))

    def rawData(self):
        self.init_setup(5)

        self.update_shape((1900,860))

    def abc(self):
        self.init_setup(2)

        self.showMaximized()


    def update_shape(self, shape):
        self.resize(shape[0], shape[1])
        self.ui_shape = shape

    def init_setup(self,index):
        self.stackedWidget.setCurrentIndex(index)
