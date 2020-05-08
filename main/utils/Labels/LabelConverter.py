__author__ = 'uid41624'
import os,sys
import sys

sys.path.insert(0, 'utils/Labels')
from main.utils.mfc510.data_load.insert_raw_chips import insert_raw_chips
from PyQt5.QtCore import *
from PyQt5 import  QtWidgets
from PyQt5 import QtCore, QtGui
import threading
from .DataMapping import DataBaseDataMapper
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtCore import QStringListModel
from .SignDescription import SignDescription
from PyQt5.QtCore import pyqtSignal
import sys


def clickable(widget):

        class Filter(QObject):

            clicked = pyqtSignal()

            def eventFilter(self, obj, event):

                if obj == widget:
                    if event.type() == QEvent.MouseButtonRelease:
                        if obj.rect().contains(event.pos()):
                            self.clicked.emit()
                            # The developer can opt for .emit(obj) to get the object within the slot.
                            return True

                return False

        filter = Filter(widget)
        widget.installEventFilter(filter)
        return filter.clicked

class pySignal(QObject):
    message = pyqtSignal(str)

class StartQT4:
    """docstring for StartQT4"""
    ExtractionComplete = pyqtSignal()

    def __init__(self, ui,parent=None):

        self.SignListFlag=False
        self.parent = parent
        self.ui = ui
        self.DataBaseDataMapperI = DataBaseDataMapper()
        self.SignDescription= SignDescription()
        self.SignList=[]
        self.CountryList=[]
        self.selectedAttribs = {}
        self.SelectedCountryList=[]
        self.SelectedSignList=[]
        self.threadActive = False
        self.ui.dumpImages.clicked.connect(self.dumpCheck)
        self.pySignal=pySignal()
        self.lightCondition=None
        self.pySignal.message.connect(self.displayMessage)
        self.dump_raw_chips=insert_raw_chips(self)
        # self.pySignal.extraction_complete.connect(self.onExtractionComplete)
#
#         self.ui.Edit.connect(self.ui.Edit, QtCore.SIGNAL("clicked()"), self.EditFunc)
# #        self.ui.SelectSign.connect(self.ui.SelectSign,QtCore.SIGNAL("clicked()"),lambda : self.DispDetails(str(self.ui.signSelect.text())))
#         self.ui.dumpImages_Chips.clicked.connect(self.dumpChips)
        self.ui.SignlistButton.clicked.connect(self.appendSignList)
        self.ui.SelectSign_image.clicked.connect(self.appendSignList_image)
        self.ui.CntryButton.clicked.connect(self.selectCountry)
        self.ui.CountryList.itemActivated.connect(self.deleteItemsCountryList)
        self.ui.CountryList_image.itemActivated.connect(self.deleteItemsCountryList)
        self.ui.SignList.itemActivated.connect(self.deleteItemsfromSignList)
        self.ui.SignList_image.itemActivated.connect(self.deleteItemsfromSignList)
        self.ui.Extract.clicked.connect(self.threading)

        self.ui.browseSignList.clicked.connect(self.onBrowseSignFileClicked)
        self.ui.selectSignFile.clicked.connect(self.readSignFromFile)

        self.ui.browseSignListForLabels.clicked.connect(lambda :self.onBrowseSignFileClicked(None))
        self.ui.selectSignListForLabels.clicked.connect(lambda :self.readSignFromFile(None))

        self.ui.browse.clicked.connect(self.onBrowseButtonClick)
        self.ui.connectToColl.clicked.connect(self.OnconnectToMongoClick)

        self.ui.ConnectToMongoDB.clicked.connect(self.OnconnectToMongoClick)
        self.ui.Update.clicked.connect( self.onUpdateButtonClick)
        self.ui.Extract_all.clicked.connect(self.threadingAll)

        self.ui.SelectAllCountry.clicked.connect(lambda :self.SelectAllCountry(None))
        self.ui.SelectAllCountry_image.clicked.connect(self.SelectAllCountry)

        self.ui.SelectAllSigns.clicked.connect(lambda :self.SelectAllSigns(None))
        self.ui.SelectAllSigns_image.clicked.connect(lambda :self.SelectAllSigns("image"))


    def dumpCheck(self):
        if self.ui.lightConditionDay.isChecked() ==self.ui.lightConditionNight.isChecked() :
            self.lightCondition = None

        elif self.ui.lightConditionNight.isChecked():
            self.lightCondition="Night"
        elif self.ui.lightConditionDay.isChecked():
            self.lightCondition="Day"
        if self.ui.rawBox.isChecked() and self.ui.chipsBox.isChecked():
            self.dump_raw_chips.dumpRawChipsThread()
        elif self.ui.rawBox.isChecked():
            self.dump_raw_chips.dumpRawThreads()
        elif self.ui.chipsBox.isChecked():
            self.dump_raw_chips.dumpChipsThread()


    def getCount(self,query):
        # self.count =
        return self.DataBaseDataMapperI.MongoDbI.find(query).count()

    def SortedSignlistUpdate(self):
       if self.threadActive:
         self.errorMessage()
       else:

           items=[]
           item=[]
           for index in xrange(self.ui.SignListDesc.count()):
                items.append(self.ui.SignListDesc.item(index))
           for i in items:
            if i.text() in self.SignList:
             item.append(i.text())
           self.SelectedSignList= self.SelectedSignList+item
           self.ui.SignList.clear()
           self.SelectedSignList=list(set(self.SelectedSignList))
           self.ui.SignList.addItems(self.SelectedSignList)
           self.ui.signSelect.clear()

    #@pyqtSlot()
    def Error(self,msg):
        self.displayMessage(msg)
        # self.displayMessage("Provide SQL PATH")

    # @pyqtSlot()
    def onExtractionComplete(self):
        self.displayMessage("Extraction Complete")




    def comboFieldSlot(self,item):
        self.ui.comboFieldValue.clear()

        dropDownList=self.DataBaseDataMapperI.getList()
        i=0

        for attribs in dropDownList:
            for values in  attribs[str(self.ui.comboField.currentText())]:
                self.ui.comboFieldValue.addItem(values)






    def readSignFromFile(self,type):
        absentSigns=[]
        absentSignsFile=open("SignsNotPresentInLookUp.txt",'w')
        if type==None:
            filePath=self.ui.SelectSignFileForLabels.text()
        else:

            filePath=self.ui.SelectSignFile.text()
        file=open(filePath,'r')
        content=file.readlines()
        signList=[x.strip() for x in content]
        self.SelectedSignList.clear()
        for sign in signList:
            if sign in self.SignList:
                self.SelectedSignList.append(sign)
            else:
                absentSignsFile.write(str(sign))
                absentSignsFile.write('\n')
        absentSignsFile.close()



        if type==None:
            self.ui.SignList.clear()
            self.ui.SignList.addItems(self.SelectedSignList)
        else:
            self.ui.SignList_image.clear()
            self.ui.SignList_image.addItems(self.SelectedSignList)

    def errorMessage(self):
        self.pySignal.message.emit("Request can not be processed ")




    def SelectAllCountry(self,type):
        if type is not None:
            self.ui.CountryList_image.clear()
            self.SelectedCountryList = list(self.CountryList)
            self.SelectedCountryList = list(set(self.SelectedCountryList))
            # self.SelectedCountryList = list(set(self.SelectedCountryList))
            self.ui.CountryList_image.addItems(self.SelectedCountryList)


        if self.threadActive:
            self.errorMessage()
        else:
            self.ui.CountryList.clear()

            self.SelectedCountryList= list(self.CountryList)
            self.SelectedCountryList=list(set(self.SelectedCountryList))
            # self.SelectedCountryList=list(set(self.SelectedCountryList))
            self.ui.CountryList.addItems(self.SelectedCountryList)

    def SelectAllSigns(self,type=None):
        if type is not None:
            self.ui.SignList_image.clear()
            self.SelectedSignList = list(self.SignList)
            self.SelectedSignList = list(set(self.SelectedSignList))
            self.ui.SignList_image.addItems(self.SelectedSignList)
            self.SelectedSignList.clear()
        if self.threadActive:
          self.errorMessage()
        else:
            self.ui.SignList.clear()
            self.SelectedSignList=list(self.SignList)
            self.SelectedSignList=list(set(self.SelectedSignList))

            self.ui.SignList.addItems(self.SelectedSignList)
            self.ui.SignList_image.addItems(self.SelectedSignList)

    def deleteItemsfromSignList(self,item):
        if self.threadActive:
          self.errorMessage()
        else:
            val=item.text()
            if len(self.SelectedSignList)==0:
                self.SelectedSignList = list(self.SignList)

                self.SelectedSignList = list(set(self.SelectedSignList))

            self.SelectedSignList.remove(val)
           # self.appendSignList()
            self.SelectedSignList=list(set(self.SelectedSignList))
            self.ui.SignList.clear()
            self.ui.SignList_image.clear()
            self.ui.SignList.addItems(self.SelectedSignList)
            self.ui.SignList_image.addItems(self.SelectedSignList)


    def MapAllData(self):
        sqlLitePath = self.ui.SqlitePath.toPlainText()
        if not sqlLitePath:
            self.pySignal.message.emit("Provide SQL PATH ")
        else:
            # t=threading.Thread(target=self.DataBaseDataMapperI.extractLabels,args=(str(sqlLitePath),self.CountryList,self.SignList))
            # #retVal = self.DataBaseDataMapperI.extractLabels(str(sqlLitePath),self.CountryList,self.SignList)
            # retVal=t.get()
            # t.start()
            # t.join()

            retVal= self.DataBaseDataMapperI.extractLabels(str(sqlLitePath),self.CountryList,self.SignList)



            # if not retVal:
            #     self.displayMessage("Mapped Sequence is not present")
            self.pySignal.extraction_complete.emit()
            self.SelectedCountryList=[]
            self.SelectedSignList= []
            self.ui.SignList.clear()
            self.ui.CountryList.clear()

    def threadingAll(self):
        if self.threadActive:
            self.errorMessage()
        else:
            self.threadActive = True
            result = threading.Thread(target=self.MapAllData)
            result.start()


    def threading(self):

        if self.threadActive:
            self.errorMessage()
        else:
            self.threadActive=True
            result=threading.Thread(target=self.MapData)
            result.start()

    def MapData(self):

        sqlLitePath = self.ui.SqlitePath.toPlainText()
        if not sqlLitePath:
             self.pySignal.message.emit("Provide SQL PATH")
             # self.pySignal.error.emit()
        else:
            retVal = self.DataBaseDataMapperI.extractLabels(str(sqlLitePath),self.SelectedCountryList,self.SelectedSignList)
            try:
                # if not retVal:
                #     self.displayMessage("Mapped Sequence is not present")
                self.SelectedCountryList=[]
                self.SelectedSignList= []
                self.pySignal.message.emit("Extraction Complete ")
                # self.ExtractionComplete.emit()
                self.ui.SignList.clear()

                self.ui.CountryList.clear()
            except:
                pass
        self.threadActive = False


    def CountryselectUpdate(self, item):
       if self.threadActive:
           self.errorMessage()
       else:
           val=item.text()
           self.SelectedCountryList.append(str(val))
           self.ui.CountryList.clear()
           self.ui.CountryList_image.clear()
           self.SelectedCountryList=list(set(self.SelectedCountryList))
           self.ui.CountryList.addItems(self.SelectedCountryList)
           self.ui.CountryList_image.addItems(self.SelectedCountryList)


    def deleteItemsCountryList(self,item):
        if self.threadActive:
            self.errorMessage()
        else:
            val=item.text()
            self.SelectedCountryList.remove(val)
            self.ui.CountryList.clear()
            self.ui.CountryList_image.clear()
            self.SelectedCountryList= list(set(self.SelectedCountryList))
            self.ui.CountryList.addItems(self.SelectedCountryList)
            self.ui.CountryList_image.addItems(self.SelectedCountryList)


    def selectCountry(self):
       if self.threadActive:
         self.errorMessage()
       else:

           val=self.ui.SelectCountry.text()
           if val:
               self.ui.SelectCountry.clear()
               self.ui.CountryList.clear()
               self.SelectedCountryList.append(str(val))
               self.SelectedCountryList = list(set(self.SelectedCountryList))
               self.ui.CountryList.addItems(self.SelectedCountryList)
               self.ui.CountryList_image.addItems(self.SelectedCountryList)
           else:
               pass

    def appendSignList(self):
        if self.threadActive:
          self.errorMessage()
        else:
            val = self.ui.SelectSignClass.text()
            if val:
                self.SelectedSignList.append(str(val))
                self.ui.SelectSignClass.clear()

                self.ui.SignList_image.clear()
                self.SelectedSignList= list(set(self.SelectedSignList))
                self.ui.SignList.addItems(self.SelectedSignList)
                self.ui.SignList_image.addItems(self.SelectedSignList)
            else:
                pass

    def appendSignList_image(self):
        if self.threadActive:
            self.errorMessage()
        else:
            val = self.ui.SelectSignClass_image.text()
            if val:
                self.SelectedSignList.append(str(val))
                self.ui.SelectSignClass_image.clear()

                self.ui.SignList_image.clear()
                self.SelectedSignList = list(set(self.SelectedSignList))
                self.ui.SignList.addItems(self.SelectedSignList)
                self.ui.SignList_image.addItems(self.SelectedSignList)
            else:
                pass

    def onBrowseButtonClick(self):
        if self.threadActive:
          self.errorMessage()
        else:
            selectedFile = QtWidgets.QFileDialog.getOpenFileName(self.ui,"Select SqlLite File","", "*.sqlite")
            if(selectedFile):
                self.ui.SqlitePath.setText(selectedFile[0])


    #     selectedFile = QtGui.QFileDialog.getExistingDirectory(self, "Select Path" )

    def onBrowseSignFileClicked(self,type):
            selectedFile = QtWidgets.QFileDialog.getOpenFileName(self.ui, "Select  File", "", "*.txt")
            if type==None:

                if (selectedFile):
                    self.ui.SelectSignFileForLabels.setText(selectedFile[0])

            else:

                if(selectedFile):
                    self.ui.SelectSignFile.setText(selectedFile[0])



    def SignlistUpdate(self, item):
        if self.threadActive:
          self.errorMessage()
        else:
           val=item.text()
           self.SelectedSignList.append(str(val))
           self.ui.SignList.clear()
           self.ui.SignList_image.clear()
           self.SelectedSignList=list(set(self.SelectedSignList))
           self.ui.SignList.addItems(self.SelectedSignList)
           self.ui.SignList_image.addItems(self.SelectedSignList)

    def OnconnectToMongoClick(self):
        if self.ui.radioMain.isChecked():
            self.signType='mainSign'
        elif self.ui.radioPVS.isChecked():
            self.signType='PVS'
        elif self.ui.radioSupplS.isChecked():
            self.signType='supplSign'
        if self.threadActive:
          self.errorMessage()
        else:

            self.mongoDBName = self.ui.MongoDataBase.toPlainText()

            if self.mongoDBName  == "":
                self.displayMessage("Mongo DB Name is Not mentioned")
                return

            HostName = self.ui.Host.toPlainText()
            if HostName == "":
                self.displayMessage("Host Name is Not mentioned")
                return

            self.CollectionName = self.ui.collectionName.toPlainText()
            self.lookUp =  self.CollectionName + "_lookUp"
            DataBasePort = self.ui.Port.toPlainText()
            if DataBasePort == "":
                self.displayMessage("DataBase Port is Not mentioned")
                return
            else:
                try:
                    PortNumber = int(DataBasePort)
                except Exception:
                    self.displayMessage("Port should be a number")
                    pass
            UserName = self.ui.UserName.toPlainText()
            Password = self.ui.Password.toPlainText()
            self.mongoUri = 'mongodb://'
            if UserName and Password:
                self.mongoUri += str(UserName) + ':' + str(Password) + '@'

            self.mongoUri += str(HostName) + ':' + str(PortNumber)

            self.mongoDBName=str(self.mongoDBName)

            isConnectionSuccess = self.DataBaseDataMapperI.performMongoDBConnection(self.mongoUri
                                                                                    ,str(self.mongoDBName)
                                                                                    ,str(self.CollectionName)
                                                                                    )
            self.DataBaseDataMapperI.getSignType(self.signType)

            if not isConnectionSuccess:
                self.displayMessage(self.DataBaseDataMapperI.getMongoDBConnectionError())
            else :

                if self.CollectionName != '':
                    try:
                        self.getUpdatedCountryAndSignList()

                    except:
                        self.pySignal.message.emit("Update LookUp collections")

                else:
                    self.pySignal.message.emit("Successfully Connected to Mongo DB")



    def upDateLookUp(self):
        sqlLitePath = self.ui.SqlitePath.toPlainText()
        if sqlLitePath:
            if self.DataBaseDataMapperI.isMongoDBConnected():
                # perform Function Calls
                self.updateSensorList(sqlLitePath)
                self.updateCountryList(sqlLitePath)
                self.updateSignClass(sqlLitePath)
                self.updateSequenceList(sqlLitePath)
                self.updateMappedSignList(sqlLitePath)
                self.pySignal.message.emit("LookUp updated")
            else:
                self.pySignal.message.emit("MongoDB is not Connected")
        else:

            self.pySignal.message.emit("Provide SQL PATH")

    def onUpdateButtonClick(self):
        if self.threadActive:
          self.errorMessage()
        else:

            t=threading.Thread(target=self.upDateLookUp)
            t.start()


    def updateCountryList(self, sqlLitePath):
        if self.threadActive:
          self.errorMessage()
        else:
            if self.ui.countryListCheckBox.isChecked():
                self.DataBaseDataMapperI.mapCountryData(str(sqlLitePath))

    def updateSignClass(self, sqlLitePath):
        if self.threadActive:
          self.errorMessage()
        else:
            if self.ui.signClassCheckBox.isChecked():
                self.DataBaseDataMapperI.mapSignClassData(str(sqlLitePath))

    def updateSequenceList(self, sqlLitePath):
        if self.threadActive:
          self.errorMessage()
        else:
            if self.ui.sequenceListCheckBox.isChecked():
                self.DataBaseDataMapperI.updateSequenceList(str(sqlLitePath))

    def updateSensorList(self, sqlLitePath):
        if self.threadActive:
          self.errorMessage()
        else:
            if self.ui.sensorListCheckBox.isChecked():
                self.DataBaseDataMapperI.updateSensorList(str(sqlLitePath))

    def updateMappedSignList(self, sqlLitePath):
        if self.threadActive:
          self.errorMessage()
        else:
            if self.ui.mappedSequenceCheckBox.isChecked():
                self.DataBaseDataMapperI.mappedSequenceData(sqlLitePath)

    def displayMessage(self, MessageToDisplay):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)

        msg.setText(MessageToDisplay)
        msg.setWindowTitle("Mongo DB Connection")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def getUpdatedCountryAndSignList(self):
        self.CountryList[:] = []
        self.SignList[:] = []
        self.ui.CountryListV.clear()
        self.ui.SignListV.clear()
        cursor = self.DataBaseDataMapperI.GetSignList()
        countryCursor =self.DataBaseDataMapperI.GetCountryList()

        for obj in countryCursor["Country List"]:
           self.CountryList.append(str(obj))

        for obj in cursor["Sign List"]:
            self.SignList.append(str(obj))

        self.ui.CountryListV.addItems(self.CountryList)
        self.ui.CountryListV_image.addItems(self.CountryList)
        self.ui.CountryListV.itemActivated.connect(self.CountryselectUpdate)
        self.ui.CountryListV_image.itemActivated.connect(self.CountryselectUpdate)
        self.ui.SignListV.addItems(self.SignList)
        self.ui.SignListV_image.addItems(self.SignList)
        self.ui.SignListV.itemActivated.connect(self.SignlistUpdate)
        self.ui.SignListV_image.itemActivated.connect(self.SignlistUpdate)
        completer = QCompleter()
        completerCountry=QCompleter()

        self.ui.SelectSignClass.setCompleter(completer)
        self.ui.SelectSignClass_image.setCompleter(completer)
        model=QStringListModel()
        completer.setModel(model)
        model.setStringList(self.SignList)
        self.ui.SelectCountry.setCompleter(completerCountry)
        self.ui.SelectCountry_image.setCompleter(completerCountry)
        modelCountry=QStringListModel()
        completerCountry.setModel(modelCountry)
        modelCountry.setStringList(self.CountryList)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    font=QtGui.QFont(myapp)
    myapp.show()
    app.exec_()