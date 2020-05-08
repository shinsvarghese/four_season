#
"""
Created on 20 Apr 2019 08:52

@projectname: FourSeasons
@filename: fs_main
@description:
@comments:
@author: Senthil
"""


import sys
from PyQt5 import QtWidgets
from PyQt5 import  QtGui
from utils.fs_mongo import MongoDB
# from fs_four_seasons import UiFourSeasons
import numpy
# import scipy
import cv2
import json
import getpass
from datetime import datetime
from .ImageProcessing import ProcessImage

class UiAnnotations:

    def __init__(self, obj_fs):

        super(UiAnnotations, self).__init__()
        self.obj_fs = obj_fs
        self.mongoDbI=MongoDB()
        self.mongoRefresh=MongoDB()
        # self.argv = argv
        self.obj_app = []
        self.bayer_patterns = [cv2.COLOR_BAYER_RG2RGB, cv2.COLOR_BAYER_BG2RGB, cv2.COLOR_BAYER_GR2RGB,
                               cv2.COLOR_BAYER_GB2RGB]
        self.obj_fs.fetch.clicked.connect(self.fetch)
        # self.obj_fs.showMaximized()
        self.obj_fs.nextBox.clicked.connect(self.nextBox)  # When Next arrow is clicked
        self.obj_fs.nextImage.clicked.connect(self.nextImage)
        # self.obj_fs.actionAnnotations.triggered.connect(self.setAnnotationPage)
        self.obj_fs.previousImage.clicked.connect(self.previousImage)
        self.obj_fs.refresh.clicked.connect(self.refresh)
        self.obj_fs.update.clicked.connect(self.update)
        # self.nextImage()
        self.obj_fs.incBrightness.clicked.connect(self.incBrightness)
        self.obj_fs.decBrightness.clicked.connect(self.decBrightness)
        self.obj_fs.previousBox.clicked.connect(self.prevBox)
        self.setAnnotationPage()
        self.brightnessIndex=0.0
        self.ProcessImageI=ProcessImage()
        # print("in constructor")
        self.complaint={}
        # self.obj_fs = []
        self.anno_status = {
            'Triangle_Signs': True,
            'Rectangle_Signs': True,
            'Circle_Signs': True,
            'Inverted_Triangle_Signs': True,
            'Pentagon_Signs': True,
            'Octagon_Signs': True,
            'Diamond_Signs':True,
            'Other_Signs': True
        }
        # self.cursor = self.mongoDbI.getData({'isModified':{'$exists':0},'image.raw': {'$exists': 1}})

    def incBrightness(self):
        try:
            self.brightnessIndex=self.brightnessIndex+5.0
            image=self.ProcessImageI.process(self.image,self.brightnessIndex)
        except Exception as e:
            print(e)
            pass
        if self.brightnessIndex == 0:
            self.dispImage(self.image)
        else:
            self.dispImage(image)

        pass

    def decBrightness(self):
        try:
            self.brightnessIndex = self.brightnessIndex - 5.0
            image=self.ProcessImageI.process(self.image, self.brightnessIndex)
        except Exception as e :
            print(e)
            pass
        if self.brightnessIndex==0:
            self.dispImage(self.image)
        else:
            self.dispImage(image)


        pass
    def displayMessage(self, MessageToDisplay):

        msg = QtWidgets.QMessageBox()

        msg.setIcon(QtWidgets.QMessageBox.Warning)


        msg.setWindowTitle("")
        if MessageToDisplay is not None:
            msg.setText(MessageToDisplay)
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        # buttonReply = QtWidgets.QMessageBox.question( 'PyQt5 message', "Do you like PyQt5?",
            msg.exec_()
        else:
            buttonReply= msg.question(self.obj_fs,'Message', "Confirm Update", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                         QtWidgets.QMessageBox.No)
            if buttonReply == QtWidgets.QMessageBox.Yes:
                return 1
            else:
                return 0
        # msg.exec_()


    def previousImage(self):

        self.retrived=self.retrived-1
        if self.retrived >= 0:
            self.cursor.rewind()



            try:
                self.data = self.cursor.skip(self.retrived-1).next()
                self.reset()
                self.refresh()
            except Exception as e:
                self.retrived = 0

                self.displayMessage("Finsihed for {0}".format(str(self.data['sourcefile'])))
                self.nextImage()
                # print (e)
                pass
        else:
            self.retrived = 0
            self.displayMessage("Finsihed for {0}".format(str(self.data['sourcefile'])))

        self.getImageData()


    def nextImage(self):


        try:

            self.data = self.cursor.next()
            # if self.retrived>0:
            #
            #     self.retrived=self.retrived  - 1
            # self.cursor.rewind()
            # self.data = self.cursor.skip(self.retrived ).next()
            self.retrived = self.retrived + 1

            self.reset()
            self.refresh()
        except Exception as e:
            print (e)
            self.displayMessage("Finsihed for {0}".format(str(self.data['sourcefile'])))
            # print (e)
            pass
        self.getImageData()

    def jumpToTimeStamp(self):

        timestamp = self.obj_fs.sign_name_2.text()
        data=self.cursor.rewind()
        for doc in data:
            self.retrived=self.retrived+1

            if int(timestamp)==doc['timestamp']:

                self.data=doc
                self.reset()
                self.refresh()
                self.getImageData()

                return


    def fetch(self):
        # print("in fetch")
        self.retrived=0

        timestamp = self.obj_fs.sign_name_2.text()
        self.sourcefile=self.obj_fs.rec_name.text()
        try:
            self.cursor = self.mongoDbI.getData({#'isModified': {'$exists': 0},
                 'sourcefile': self.sourcefile,
                 'image.raw': {'$exists': 1}}).sort('timestamp', 1)

            if timestamp:
                self.jumpToTimeStamp()

            else:

                self.docCount=self.cursor.count()

                self.nextImage()
        except Exception as e:
            pass

    def complaints(self):
        self.complaintList=[]

        if self.obj_fs.Wrong_Shape.isChecked():
            self.complaintList.append("Wrong Shape")
        if self.obj_fs.Wrong_Sign_Class.isChecked():
            self.complaintList.append("Wrong SignClass")
        if self.obj_fs.WrongBB.isChecked():
            self.complaintList.append("Wrong Bounding Box")
        if self.obj_fs.Wrong_attrib.isChecked():
            self.complaintList.append("Wrong Attributes")
        if len(self.complaintList) >0:
            if self.data['_id'] in self.complaint.keys():
                pass
            else:
                self.complaint[self.data['_id']] = []
            complaint= {
                    'SignID(' + str(self.data['annotations']['boxlabel'][self.counter]['signId']) + ')': self.complaintList}
            # if complaint not in self.complaint:
            if complaint.keys() not in [x.keys() for x in self.complaint[self.data["_id"]]]:
                self.complaint[self.data['_id']].append(complaint)
        # print (self.complaint)

    def setAnnotationPage(self):
        self.obj_fs.init_setup(3)

    def refresh(self):

        try:
            self.obj_fs.count.setText(str(self.retrived) + "/" + str(self.docCount))
            cursor = self.mongoRefresh.getSingleData({'_id': self.data['_id']})

            self.data=cursor.next()
            annotated_signs=self.data['annotations']['anno_completed']
        # print (self.data)

        except:
            self.obj_fs.isModified.clear()
            return
        # self.reset()
        try:
            if annotated_signs['Triangle_Signs'] == True:
                self.obj_fs.Triangle_Signs.setChecked(True)
            else:
                self.obj_fs.Triangle_Signs.setChecked(False)
        except:
            pass
        try:
            if annotated_signs['Rectangle_Signs'] == True:
                self.obj_fs.Rectangle_Signs.setChecked(True)
            else:
                self.obj_fs.Rectangle_Signs.setChecked(False)
        except:
            pass
        try:
            if annotated_signs['Circle_Signs'] == True:
                self.obj_fs.Circle_Signs_2.setChecked(True)
            else:
                self.obj_fs.Circle_Signs_2.setChecked(False)
        except:
            pass
        try:
            if annotated_signs['Inverted_Triangle_Signs'] == True:
                self.obj_fs.Inv_Triangle_Signs.setChecked(True)
            else:
                self.obj_fs.Inv_Triangle_Signs.setChecked(False)
        except:
            pass
        try:
            if annotated_signs['Octagon_Signs'] == True:
                self.obj_fs.Octagon_Signs.setChecked(True)
            else:
                self.obj_fs.Octagon_Signs.setChecked(False)
        except:
            pass
        try:
            if annotated_signs['Pentagon_Signs'] == True:
                self.obj_fs.Pentagon_Signs.setChecked(True)
            else:
                self.obj_fs.Pentagon_Signs.setChecked(False)
        except:
            pass
        try:
            if annotated_signs['Other_Signs'] == True:
                self.obj_fs.Other_Signs.setChecked(True)
            else:
                self.obj_fs.Other_Signs.setChecked(False)
        except:
            pass
        try:
            if annotated_signs['Diamond_Signs'] == True:
                self.obj_fs.Diamond_Signs.setChecked(True)
            else:
                self.obj_fs.Diamond_Signs.setChecked(False)
        except:
            pass
        try:
            self.obj_fs.isModified.clear()
            self.obj_fs.isModified.setText("Modified by : "+str(self.data['isModified']['modified_by']))
        except:
            pass
    def update(self):
        try:
            self.compFile = open('Complaint.json', 'w+')
            self.complaints()
            if self.obj_fs.Triangle_Signs.isChecked():
                self.anno_status['Triangle_Signs']=True
            else:
                self.anno_status['Triangle_Signs'] = False

            if self.obj_fs.Inv_Triangle_Signs.isChecked():
                self.anno_status['Inverted_Triangle_Signs'] = True
            else:
                self.anno_status['Inverted_Triangle_Signs'] = False
            if self.obj_fs.Circle_Signs_2.isChecked():
                self.anno_status['Circle_Signs'] = True
            else:
                self.anno_status['Circle_Signs'] = False
            if self.obj_fs.Rectangle_Signs.isChecked():
                self.anno_status['Rectangle_Signs'] = True
            else:
                self.anno_status['Rectangle_Signs'] = False
            if self.obj_fs.Octagon_Signs.isChecked():
                self.anno_status['Octagon_Signs'] = True
            else:
                self.anno_status['Octagon_Signs'] = False
            if self.obj_fs.Diamond_Signs.isChecked():
                self.anno_status['Diamond_Signs'] = True
            else:
                self.anno_status['Diamond_Signs'] = False

            if self.obj_fs.Pentagon_Signs.isChecked():
                self.anno_status['Pentagon_Signs'] = True
            else:
                self.anno_status['Pentagon_Signs'] = False
            if self.obj_fs.Other_Signs.isChecked():
                self.anno_status['Other_Signs'] = True
            else:
                self.anno_status['Other_Signs'] = False
            self.data['annotations']['anno_completed']=self.anno_status

            # print (self.complaint)
            self.data['isModified']={'modified_time':datetime.now(),'modified_by': getpass.getuser()}
            json.dump(self.complaint, self.compFile)
            self.compFile.close()
            if self.displayMessage(None):
                self.mongoDbI.update(self.data)
            else:
                pass

        except:
            pass

    def reseTcomplaints(self):
        self.obj_fs.Wrong_Shape.setChecked(False)
        self.obj_fs.WrongBB.setChecked(False)
        self.obj_fs.Wrong_attrib.setChecked(False)
        self.obj_fs.Wrong_Sign_Class.setChecked(False)

    def reset(self):
        self.reseTcomplaints()

        self.obj_fs.Other_Signs.setChecked(True)
        self.obj_fs.Triangle_Signs.setChecked(True)
        self.obj_fs.Inv_Triangle_Signs.setChecked(True)
        self.obj_fs.Rectangle_Signs.setChecked(True)
        self.obj_fs.Circle_Signs_2.setChecked(True)
        self.obj_fs.Octagon_Signs.setChecked(True)
        self.obj_fs.Pentagon_Signs.setChecked(True)
        self.obj_fs.Diamond_Signs.setChecked(True)


    def putText(self):
        x0 = self.data['annotations']['boxlabel'][self.counter]['x0']
        y0 = self.data['annotations']['boxlabel'][self.counter]['y0']
        x1 = self.data['annotations']['boxlabel'][self.counter]['x1']
        y1 = self.data['annotations']['boxlabel'][self.counter]['y1']
        image = self.image.copy()

        cv2.rectangle(image, (x0, y0),
                      (x1, y1), (255, 0, 0), 2)
        self.dispImage(image)
        # print("counter in Next", self.counter)
        self.obj_fs.sign_name.setText(
            self.data['annotations']['boxlabel'][self.counter]['attributes']['sign_class']['value'])
        self.obj_fs.sign_shape.setText(self.data['annotations']['boxlabel'][self.counter]['class'])
        self.obj_fs.rec_name.setText(str(self.data['sourcefile']))
        self.obj_fs.sign_name_2.setText(str(self.data['timestamp']))
        self.obj_fs.x0_3.setText(str(x0))
        self.obj_fs.y0_3.setText(str(y0))
        self.obj_fs.x1.setText(str(x1))
        self.obj_fs.y1.setText(str(y1))
        self.obj_fs.signId.setText(str(self.data['annotations']['boxlabel'][self.counter]['signId']))
        self.obj_fs.Height.setText(str(self.data['annotations']['boxlabel'][self.counter]['height']))
        self.obj_fs.width.setText(str(self.data['annotations']['boxlabel'][self.counter]['width']))
        self.obj_fs.boxLabelIndex.clear()
        self.obj_fs.boxLabelIndex.insertPlainText(
            str(self.counter + 1) + '/' + str(len(self.data['annotations']['boxlabel'])))
        # annotated_signs = list(self.data['annotations']['anno_completed'].keys())
        annotated_signs=self.data['annotations']['anno_completed']


        try:
            if  annotated_signs['Triangle_Signs'] == True:
                self.obj_fs.Triangle_Signs.setChecked(True)
        except:
            pass
        try:
            if annotated_signs['Rectangle_Signs'] == True:
                    self.obj_fs.Rectangle_Signs.setChecked(True)
        except:
            pass
        try:
            if annotated_signs['Circle_Signs'] == True:
                    self.obj_fs.Circle_Signs_2.setChecked(True)
        except:
            pass
        try:
            if annotated_signs['Inverted_Triangle_Signs'] == True:
                       self.obj_fs.Inv_Triangle_Signs.setChecked(True)
        except:
            pass
        try:
            if annotated_signs['Octagon_Signs'] == True:
                        self.obj_fs.Octagon_Signs.setChecked(True)
        except:
            pass
        try:
            if annotated_signs['Pentagon_Signs'] == True:
                       self.obj_fs.Pentagon_Signs.setChecked(True)
        except:
            pass
        try:
            if annotated_signs['Other_Signs'] == True:

                     self.obj_fs.Other_Signs.setChecked(True)
        except:
            pass
        try:
            if annotated_signs['Diamond_Signs'] == True:
                         self.obj_fs.Diamond_Signs.setChecked(True)
        except:
            pass



    def prevBox(self):
        self.reseTcomplaints()
        self.counter -= 1
        if self.counter >= 0 and self.Label_Start == False:
            # print("counter in Prev", self.counter)
            self.Label_End = False
            self.putText()

        if self.counter <= 0:
            self.counter = 0
            self.Label_Start = True
            self.Label_End = False

    def nextBox(self):

        self.complaints()
        self.reseTcomplaints()
        try:
            if self.counter < len(self.data['annotations']['boxlabel']) and self.Label_End == False:
                self.Label_Start = False
                self.counter += 1
                self.putText()

            if self.counter == len(self.data['annotations']['boxlabel'])-1 :
                # self.counter = len(self.data['annotations']['boxlabel']) - 1
                self.Label_End = True
                self.Label_Start = False
        except:
            pass
            # msg = QMessageBox()
            # msg.setIcon(QMessageBox.Information)
            # msg.setWindowTitle("Please press Next button")
            # msg.setText("Please load image first")
            # QMessageBox.about(self, "Title", "Please select an image first")




    def getImageData(self):
        self.counter = -1
        self.Label_Start = True
        self.Label_End = False
        self.brightnessIndex =0

        hash = self.data['image']['raw']['hash']
        image = self.mongoDbI.getImage(hash)
        image = image / (image.max() / 255)
        image = image.astype(numpy.uint8)

        self.image = cv2.cvtColor(image, self.bayer_patterns[3])

        for coords in self.data['annotations']['boxlabel']:
            cv2.rectangle(self.image, (int(coords['x0']), int(coords['y0'])),
                          (int(coords['x1']), int(coords['y1'])), (255, 255, 255), 2)

        self.dispImage(self.image)

        self.nextBox()

    def dispImage(self,image):
        img = QtGui.QImage(image.data, image.shape[1], image.shape[0], QtGui.QImage.Format_RGB888)
        img.scaledToWidth(self.obj_fs.imageLabel.width())
        img.scaledToHeight(self.obj_fs.imageLabel.height())
        pixmap = QtGui.QPixmap(img)
        self.obj_fs.imageLabel.setScaledContents(True)
        self.obj_fs.imageLabel.setPixmap(pixmap)

