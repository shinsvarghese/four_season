__author__ = 'uidq1602'

from PyQt4 import QtGui

class BrowseButton():
    def __init__(self):
        self.isValidPath = True

    def onBrowseButtonClick(self):
        selectedFile = QtGui.QFileDialog.getOpenFileName(self)
        print (selectedFile)


BrowseButtonI = BrowseButton();
BrowseButtonI.onBrowseButtonClick();
