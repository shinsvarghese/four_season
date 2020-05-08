import os
import threading
from main.utils.mfc510.chips.run_chips_mfc510 import mainProcess
query = {"image.raw": {"$exists": 0}, 'sourcefolder': {'$nin':
    [
        "N/A",
        "N/A two or more hits!"
    ]}
         }
class dump_raw_chips:
    def __init__(self,label_obj):
        self.label_obj=label_obj

    def dumpRawChipsThread(self):
        t = threading.Thread(target=self.dumpRawChips)
        t.start()


    def dumpRawChips(self):
        limit = 0
        skip = 0
        ChipsCounter = 0

        if self.label_obj.lightCondition != None:
            query["annotations.framelabel.light_conditions.value"] = str(self.label_obj.lightCondition)
        if len(self.label_obj.SelectedCountryList) > 0:
            query['annotations.framelabel.country.value'] = {'$in': self.label_obj.SelectedCountryList}
        if len(self.label_obj.SelectedSignList) > 0:
            query['annotations.boxlabel.attributes.sign_class.value'] = {'$in': self.label_obj.SelectedSignList}
        count = self.label_obj.DataBaseDataMapperI.MongoDbI.find(query).count()
        maxCores = 2
        rem = count % maxCores
        # print(count)
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
            tList[i]['raw'] = threading.Thread(target=self.label_obj.dumpRaw, args=[tList[i]['limit'], tList[i]['skip'], i])
            tList[i]['raw'].start()

        while chipsThreadInitiated:
            for i in range(maxCores):
                if tList[i]['raw'].is_alive() == False and 'chips' not in tList[i].keys():
                    print('raw data dump finished in thread...{0}'.format(str(i)))
                    tList[i]['chips'] = threading.Thread(target=mainProcess,
                                                         args=[self.label_obj.DataBaseDataMapperI.MongoDbI, self.label_obj.SelectedSignList,
                                                               self.label_obj.SelectedCountryList, self.label_obj.mongoUri
                                                             , self.label_obj.mongoDBName
                                                             , self.label_obj.CollectionName, tList[i]['limit'], tList[i]['skip'], i,
                                                               self.label_obj.lightCondition])
                    tList[i]['chips'].start()
                    ChipsCounter = ChipsCounter + 1
            if ChipsCounter == maxCores:
                chipsThreadInitiated = False


    def dumpChipsThread(self, limit=0, skip=0):
        count = self.label_obj.ui.signCount.text()
        if count != "":
            limit = count
        t1 = threading.Thread(target=mainProcess,
                              args=[self.label_obj.DataBaseDataMapperI.MongoDbI, self.label_obj.SelectedSignList, self.label_obj.SelectedCountryList,
                                    self.label_obj.mongoUri
                                  , self.label_obj.mongoDBName
                                  , self.label_obj.CollectionName, limit, skip, None, self.label_obj.lightCondition])

        t1.start()


    def dumpRawThreads(self):
        print("Raw data extraction initiated")
        t1 = threading.Thread(target=self.dumpRaw)
        t1.start()


    def dumpRaw(self, limit=0, skip=0, thread=None):
        if thread != None:
            print("raw dump started in thread..{0}".format(str(thread)))
        else:
            print("raw dump started")
        try:
            count = self.label_obj.ui.signCount.text()
            if count != "":
                limit = count
            #
            # dirname = os.getcwd()+"\\dlls"
            # raw_image_extractor=get_dll_path()
            #
            # rawDumpCommand= r" --uri {0} --c {1} --d {2} --countryList {4} --signList {3} --limit {5} --skip {6} --lightCondition {7} --signCount {8}".format(str(self.mongoUri),str(self.CollectionName),str(self.mongoDBName),str(self.SelectedSignList).replace(" ",''),str(self.SelectedCountryList).replace(" ",''),limit,skip,self.lightCondition,str(limit))
            #
            # os.system(raw_image_extractor + rawDumpCommand)

            # # for pyinstaller uncomment the below lines
            if len(self.label_obj.SelectedSignList) > 2400:
                self.label_obj.SelectedSignList = []
            rawDumpCommand = r"export_images_from_recfile.exe --uri {0} --c {1} --d {2}" \
                             r" --countryList {4} --signList {3} --limit {5} --skip {6}" \
                             r" --lightCondition {7} --signCount {8}".format(
                str(self.label_obj.mongoUri), str(self.label_obj.CollectionName), str(self.label_obj.mongoDBName),
                str(self.label_obj.SelectedSignList).replace(" ", ''), str(self.label_obj.SelectedCountryList).replace(" ", ''), limit,
                skip, self.label_obj.lightCondition, str(limit))
            os.system(rawDumpCommand)

            if thread == None:
                print("raw dump completed")
            return

        except Exception as e:
            print("exception : ", e)
            pass
