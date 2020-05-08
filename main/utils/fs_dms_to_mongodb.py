#
"""
Created on 24 Apr 2019 8:29 AM
 
@projectname: FourSeasons
@filename: fs_dms_to_mongodb
@description: 
@comments: 
@author: uidn9667
"""


from PyQt5 import QtWidgets
from .fs_defines import UiShape
from .fs_mongo import MongoDB

class UiDMStoMongoDB():

    def __init__(self, ui):
        super(UiDMStoMongoDB, self).__init__()
        self.ui = ui
        self.ui.pushButtonSynchDMS2MongoDB.clicked.connect(self.temp)
        self.ui.actionDMS_to_MongoDB.triggered.connect(self.act)


    def act(self):

        self.ui.init_setup(0)


    def update_shape(self):
        self.ui.resize(UiShape.small[0], UiShape.small[1])
        self.ui.ui_shape = UiShape.small

