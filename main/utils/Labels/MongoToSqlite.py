import pymongo
import sqlite3

cl= pymongo.MongoClient('ozd0127u',2345)
db=cl['Labels']
col=db['Latest']

content=col.find_one({})
# print content

cur=sqlite3.connect('D:\shins.sqlite')
sqlString = 'create table shins ('


sqlString=sqlString+')'
sqlString=sqlString%tuple(content.keys())
cur.execute(sqlString)
#
# insert='insert into shins(sourcefolder) values ("'+content['sourcefile']+'")'


