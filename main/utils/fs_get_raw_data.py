
import sys
from PyQt5 import QtWidgets
from PyQt5 import  QtGui
from .fs_mongo import MongoDB
# from fs_four_seasons import UiFourSeasons
import numpy
# from rawImageToMongo.mongodb.export_images_from_recfile import getRawData
# import scipy
import cv2
import json
import getpass
from datetime import datetime

class UIRawData:

    def __init__(self, obj_fs):

        super(UIRawData, self).__init__()
        self.ui = obj_fs
        # getRawDataI=getRawData()
        self.SignList = []
        self.CountryList = []
        self.selectedAttribs = {}
        self.SelectedCountryList = []
        self.SelectedSignList = []
        self.ui.CntryButton_image.clicked.connect(self.selectCountry)
        # self.ui.dumpImages.clicked.connect(self.dumpImages)

        # self.ui.CountryList_image.itemActivated.connect(self.deleteItemsCountryList)

        # self.ui.SignList_image.itemActivated.connect(self.deleteItemsfromSignList)

        self.ui.SelectAllCountry_image.clicked.connect(self.SelectAllCountry)
        self.ui.SelectAllSigns_image.clicked.connect(self.SelectAllSigns)



    def dumpImages(self):
        self.getRawDataI.process(self.SelectedSignList,self.SelectedCountryList)


    #
    # def comboFieldSlot(self,item):
    #     self.ui.comboFieldValue.clear()
    #
    #     dropDownList=self.DataBaseDataMapperI.getList()
    #     i=0
    #
    #     for attribs in dropDownList:
    #         for values in  attribs[str(self.ui.comboField.currentText())]:
    #             self.ui.comboFieldValue.addItem(values)
    #
    #









    def errorMessage(self):
        self.displayMessage("Request can not be processed ")




    def SelectAllCountry(self):

            self.ui.CountryList.clear()
            self.SelectedCountryList= list(self.CountryList)
            self.SelectedCountryList=list(set(self.SelectedCountryList))
            self.ui.CountryList_image.addItems(self.SelectedCountryList)

    def SelectAllSigns(self):

            self.ui.SignList.clear()
            self.SelectedSignList=list(self.SignList)
            self.SelectedSignList=list(set(self.SelectedSignList))
            self.ui.SignList_image.addItems(self.SelectedSignList)

    def deleteItemsfromSignList(self,item):

            val=item.text()
            self.SelectedSignList.remove(val)
           # self.appendSignList()
            self.SelectedSignList=list(set(self.SelectedSignList))
            self.ui.SignList_image.clear()
            self.ui.SignList_image.addItems(self.SelectedSignList)





    def CountryselectUpdate(self, item):

           val=item.text()
           self.SelectedCountryList.append(str(val))
           self.ui.CountryList_image.clear()
           self.SelectedCountryList=list(set(self.SelectedCountryList))

           self.ui.CountryList_image.addItems(self.SelectedCountryList)


    def deleteItemsCountryList(self,item):

            val=item.text()

            self.SelectedCountryList.remove(val)
            self.ui.CountryList.clear()
            self.ui.CountryList_image.clear()
            self.SelectedCountryList= list(set(self.SelectedCountryList))
            self.ui.CountryList.addItems(self.SelectedCountryList)
            self.ui.CountryList_image.addItems(self.SelectedCountryList)


    def selectCountry(self):


           val=self.ui.SelectCountry.text()
           if val:
               self.ui.SelectCountry.clear()
               self.ui.CountryList_image.clear()
               self.SelectedCountryList.append(str(val))
               self.SelectedCountryList = list(set(self.SelectedCountryList))
               self.ui.CountryList_image.addItems(self.SelectedCountryList)
           else:
               pass

    def appendSignList(self):

            val = self.ui.SelectSignClass_image.text()
            if val:
                self.SelectedSignList.append(str(val))
                self.ui.SelectSignClass_image.clear()
                self.ui.SignList.clear()
                self.ui.SignList_image.clear()
                self.SelectedSignList= list(set(self.SelectedSignList))
                self.ui.SignList.addItems(self.SelectedSignList)
                self.ui.SignList_image.addItems(self.SelectedSignList)
            else:
                pass









    def SignlistUpdate(self, item):

           val=item.text()
           self.SelectedSignList.append(str(val))
           self.ui.SignList.clear()
           self.ui.SignList_image.clear()
           self.SelectedSignList=list(set(self.SelectedSignList))
           self.ui.SignList.addItems(self.SelectedSignList)
           self.ui.SignList_image.addItems(self.SelectedSignList)