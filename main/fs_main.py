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
import multiprocessing
# import sys
# sys.path.insert(0, 'utils/')
from utils.fs_four_seasons import UiFourSeasons
import types


class MainApp:

    def __init__(self, argv):
        super(MainApp, self).__init__()
        self.argv = argv
        self.obj_app = []
        self.obj_fs = []

    def launch(self):
        self.obj_app = QtWidgets.QApplication(self.argv)
        self.obj_fs = UiFourSeasons()
        self.obj_fs.show()
        self.obj_app.exec_()
def imports():
    for name, val in globals().items():
        if isinstance(val, types.ModuleType):
            yield val.__name__

if __name__ == "__main__":
    multiprocessing.freeze_support()
    obj_main_app = MainApp(sys.argv)
    obj_main_app.launch()
