import pymongo
import json
col_local=pymongo.MongoClient()['sr_labels']['SignDescription']
col_main=pymongo.MongoClient('ozd0127u',27018)['Labels']['SignDescription']
file=open('D:\\signDesc.json','w')
sign_desc = dict()
for doc in col_local.find():
    try:

        sign_desc[doc['_id']]=doc
    except:
        continue
json.dump(sign_desc,file,indent=4)
    # col_local.insert(doc)
