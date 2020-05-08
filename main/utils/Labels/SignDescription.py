
from xlrd import open_workbook
import pymongo


class SignDescription:
   def LoadFromXl(self, XlsPath, collectionName, dbName='Labels'):

      client = pymongo.MongoClient()
      db = client[str(dbName)]
      collection = db[str(collectionName)]

      wb = open_workbook(XlsPath)
      sheet = wb.sheet_by_index(8)

      # for sheet in wb.sheets():
      ##  break
      number_of_rows = sheet.nrows
      number_of_columns = sheet.ncols
      print (number_of_rows)
      print (collectionName)
      print (dbName)
      items = {}

      data = {}
      LookUp={}

      for row in range(1, number_of_rows):
         values = {}

         if sheet.cell(row, 0).value and sheet.cell(row, 4).value:
            values['sign_name'] = str(sheet.cell(row, 0).value)
            values['sign_type'] = str(sheet.cell(row, 3).value)
            values['shape'] = str(sheet.cell(row, 4).value)
            values['background_Color'] = str(sheet.cell(row, 5).value)
            values['foreground_Color'] = str(sheet.cell(row, 6).value)
            values['border_Present'] = str(sheet.cell(row, 7).value)
            values['border_Color'] = str(sheet.cell(row, 8).value)
            values['endLine_Present'] = str(sheet.cell(row, 9).value)
            values['endLine_Color'] = str(sheet.cell(row, 10).value)
            values['endLine_Orientation'] = str(sheet.cell(row, 11).value)
            values['endLine_Content'] = str(sheet.cell(row, 12).value)

            items['_id'] = str(sheet.cell(row, 0).value)
            items['data'] = values
            if collection.find_one({"_id": str(sheet.cell(row, 0).value)}):
               collection.delete_one({"_id":str(sheet.cell(row, 0).value)})
            collection.insert_one(items)
      isExisting = collection.find_one({"_id": "LookUp"})
      check = collection.find_one({})
      if isExisting:
         pass
      else:
         LookUp['_id'] = "LookUp"
         for i in check['data']:
            if i == "sign_name":
               pass
            else:
               a = "data." + i
               LookUp[i] = list(collection.distinct(a))
               print (list(collection.distinct(a)))

               # print a
         collection.insert_one(LookUp)
      print ("inserted")




            # item = Arm(*values)
            # items.append(item)
            # i=i+1
            # for item in items:
            #print (item)

            #    print("Accessing one single value (eg. DSPName): {0}".format(item.dsp_name))
