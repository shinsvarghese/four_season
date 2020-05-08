__author__ = 'uidq1602'

import datetime
import getpass

class UserAndTimeInfo:

    def __init__(self):
        self.labelCreationDate = 'creation_date'
        self.labelModifiedDate = 'modified_date'
        self.labelModifiedByUser = 'modified_user'

    def updateLabelCreationInfo(self, MongoData, isEntryExisting = False):
        if not isEntryExisting:
            MongoData[self.labelCreationDate] = datetime.datetime.now()

        MongoData[self.labelModifiedDate] = datetime.datetime.now()
        MongoData[self.labelModifiedByUser] = getpass.getuser()
