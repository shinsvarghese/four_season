import os
import threading
from main.utils.mfc510.data_load.insert_raw_images import dump_raw_images
from main.utils.mfc510.chips.run_chips_mfc510 import run_chips
dll_name="export_images_from_recfile.exe"
maxCores = 2

def get_dll_path():

    dll_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dlls","raw_extractor"))
    dll_path = os.path.join(dll_folder, dll_name)
    #os.environ['PATH'] = dll_folder + ';' + os.environ['PATH']
    #os.chdir(dll_folder)
    return dll_path


query = {"image.raw": {"$exists": 0}, 'sourcefolder': {'$nin':
    [
        "N/A",
        "N/A two or more hits!"
    ]}
         }
#self.ui.dumpImages.clicked.connect(self.dumpCheck)
# def dumpCheck(self):
#     if self.ui.lightConditionDay.isChecked() == self.ui.lightConditionNight.isChecked():
#         self.lightCondition = None
#
#     elif self.ui.lightConditionNight.isChecked():
#         self.lightCondition = "Night"
#     elif self.ui.lightConditionDay.isChecked():
#         self.lightCondition = "Day"
#     if self.ui.rawBox.isChecked() and self.ui.chipsBox.isChecked():
#         self.dump_raw_chips.dumpRawChipsThread()
#     elif self.ui.rawBox.isChecked():
#         self.dump_raw_chips.dumpRawThreads()
#     elif self.ui.chipsBox.isChecked():
#         self.dump_raw_chips.dumpChipsThread()


class insert_raw_chips:
    def __init__(self, label_obj):
        self.label_obj = label_obj

    def dumpRawChipsThread(self):
        t = threading.Thread(target=self.dumpRawChips)
        t.start()

    def dumpRawChips(self):

        ChipsCounter = 0

        if self.label_obj.lightCondition != None:
            query["annotations.framelabel.light_conditions.value"] = str(self.label_obj.lightCondition)
        if len(self.label_obj.SelectedCountryList) > 0:
            query['annotations.framelabel.country.value'] = {'$in': self.label_obj.SelectedCountryList}
        if len(self.label_obj.SelectedSignList) > 0:
            query['annotations.boxlabel.attributes.sign_class.value'] = {'$in': self.label_obj.SelectedSignList}
        count = self.label_obj.DataBaseDataMapperI.MongoDbI.find(query).count()

        rem = count % maxCores
        chipsThreadInitiated = True
        tList = {}

        if rem == 0:
            for i in range(maxCores):
                tList[i] = {'limit': int(count / maxCores), 'skip': int((count / maxCores) * i)}
        else:
            for i in range(maxCores - 1):
                tList[i] = {'limit': int(count / maxCores), 'skip': int((count / maxCores) * i)}

            tList[maxCores - 1] = {'limit': int(count / maxCores) + rem, 'skip': int(count / maxCores) * (maxCores - 1)}

        for i in range(0, maxCores):
            tList[i]['raw'] = threading.Thread(target=dump_raw_images,
                                               args=[self.label_obj,tList[i]['limit'], tList[i]['skip'], i])
            tList[i]['raw'].start()

        while chipsThreadInitiated:
            for i in range(maxCores):
                if tList[i]['raw'].is_alive() == False and 'chips' not in tList[i].keys():
                    print('raw data dump finished in thread...{0}'.format(str(i)))
                    tList[i]['chips'] = threading.Thread(target=run_chips,
                                                         args=[self.label_obj.DataBaseDataMapperI.MongoDbI,
                                                               self.label_obj.SelectedSignList,
                                                               self.label_obj.SelectedCountryList,
                                                               self.label_obj.mongoUri
                                                             , self.label_obj.mongoDBName
                                                             , self.label_obj.CollectionName, tList[i]['limit'],
                                                               tList[i]['skip'], i,
                                                               self.label_obj.lightCondition])
                    tList[i]['chips'].start()
                    ChipsCounter = ChipsCounter + 1
            if ChipsCounter == maxCores:
                chipsThreadInitiated = False

    def dumpChipsThread(self, limit=0, skip=0):
        count = self.label_obj.ui.signCount.text()
        if count != "":
            limit = count
        t1 = threading.Thread(target=run_chips,
                              args=[self.label_obj.DataBaseDataMapperI.MongoDbI, self.label_obj.SelectedSignList,
                                    self.label_obj.SelectedCountryList,
                                    self.label_obj.mongoUri
                                  , self.label_obj.mongoDBName
                                  , self.label_obj.CollectionName, limit, skip, None, self.label_obj.lightCondition])

        t1.start()

    def dumpRawThreads(self):
        print("Raw data extraction initiated")
        t1 = threading.Thread(target=dump_raw_images, args=[self.label_obj])
        t1.start()
