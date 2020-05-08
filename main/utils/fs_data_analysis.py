import os
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import pandas as pd
from utils.fs_data_processing import DataProcessing
from utils.config import VisualizationConfig


class DataAnalysis(object):

    def __init__(self, ui):
        super(DataAnalysis, self).__init__()
        self.ui = ui
        self.selected_shape_list = []
        self.selected_sign_list = []
        self.selected_country_list = []
        self.data_processing = DataProcessing()
        self.ui.comboBox_7.currentIndexChanged.connect(self.profile)
        self.ui.comboBox_3.addItems(VisualizationConfig.ComboBox3_Items)
        self.ui.comboBox_3.currentIndexChanged.connect(self.collection)
        self.ui.listWidget_3.itemClicked.connect(self.shape_attribute)
        self.ui.listWidget_2.itemClicked.connect(self.sign_attribute)
        self.ui.listWidget.itemClicked.connect(self.country_attribute)
        self.ui.pushButton_2.clicked.connect(self.sign_count)
        self.ui.pushButton.clicked.connect(lambda: self.plot("Bar_graph", False))
        self.ui.pushButton_3.clicked.connect(lambda: self.plot("Bar_graph", True))
        self.ui.pushButton_4.clicked.connect(self.select_all_shape_items)
        self.ui.pushButton_5.clicked.connect(self.deselect_all_shape_items)
        self.ui.pushButton_6.clicked.connect(self.select_all_sign_items)
        self.ui.pushButton_7.clicked.connect(self.deselect_all_sign_items)
        self.ui.pushButton_8.clicked.connect(self.select_all_country_items)
        self.ui.pushButton_9.clicked.connect(self.deselect_all_country_items)
        self.ui.pushButton_10.clicked.connect(self.export_csv)
        self.ui.pushButton_11.clicked.connect(self.reset_bin_table)
        self.ui.checkBox.toggled.connect(self.shape_attribute)
        self.ui.checkBox_2.toggled.connect(self.shape_attribute)

    def deselect_all_shape_items(self):
        if self.ui.listWidget_3.count() == 0:
            DataAnalysis.error_message("Please select Collection List")
        else:
            for i in range(self.ui.listWidget_3.count()):
                item = self.ui.listWidget_3.item(i)
                item.setSelected(False)
        self.shape_attribute()

    def select_all_shape_items(self):
        if self.ui.listWidget_3.count() == 0:
            DataAnalysis.error_message("Please select Collection List")
        else:
            for i in range(self.ui.listWidget_3.count()):
                item = self.ui.listWidget_3.item(i)
                item.setSelected(True)
        self.shape_attribute()

    def deselect_all_sign_items(self):
        if self.ui.listWidget_2.count() == 0:
            DataAnalysis.error_message("Please select both Shape Attribute and Checkbox")
        else:

            for i in range(self.ui.listWidget_2.count()):
                item = self.ui.listWidget_2.item(i)
                item.setSelected(False)
        self.sign_attribute()

    def select_all_sign_items(self):
        if self.ui.listWidget_2.count() == 0:
            DataAnalysis.error_message("Please select both Shape Attribute and Checkbox")
        else:

            for i in range(self.ui.listWidget_2.count()):
                item = self.ui.listWidget_2.item(i)
                item.setSelected(True)
        self.sign_attribute()

    def deselect_all_country_items(self):
        if self.ui.listWidget.count() == 0:
            DataAnalysis.error_message("Please select Sign ID")
        else:

            for i in range(self.ui.listWidget.count()):
                item = self.ui.listWidget.item(i)
                item.setSelected(False)
        self.country_attribute()

    def select_all_country_items(self):
        if self.ui.listWidget.count() == 0:
            DataAnalysis.error_message("Please select Sign ID")
        else:

            for i in range(self.ui.listWidget.count()):
                item = self.ui.listWidget.item(i)
                item.setSelected(True)
        self.country_attribute()

    @staticmethod
    def error_message(error_message):
        msg = QtWidgets.QMessageBox()
        msg.setStyleSheet("QLabel{min-width:200 px; font-size: 16px;} ")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(error_message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def collection(self):
        try:
            if self.ui.comboBox_3.currentText() == 'Collection List':
                self.ui.listWidget_3.clear()
                DataAnalysis.error_message("Please Select Collection list")
                self.ui.listWidget_3.clear()

            else:
                self.ui.tableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem(str(self.ui.comboBox_3.currentText())))
                self.ui.tableWidget.show()
                self.ui.listWidget_3.clear()
                self.ui.listWidget_2.clear()
                self.ui.listWidget.clear()
                self.ui.tableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem(""))
                self.ui.tableWidget.setItem(0, 3, QtWidgets.QTableWidgetItem(""))
                self.ui.tableWidget.setItem(0, 4, QtWidgets.QTableWidgetItem(""))
                self.ui.tableWidget_3.setItem(0, 0, QtWidgets.QTableWidgetItem(""))
                self.ui.tableWidget_3.setItem(0, 1, QtWidgets.QTableWidgetItem(""))
                self.ui.tableWidget_3.setItem(0, 2, QtWidgets.QTableWidgetItem(""))
                self.ui.tableWidget_2.setItem(1, -1, QtWidgets.QTableWidgetItem(""))
                self.ui.label_6.clear()
                self.ui.tableWidget.show()
                self.ui.label_5.clear()
                if os.path.exists(str(self.ui.comboBox_3.currentText())):
                    shape_list = self.data_processing.execute_query("class", str(self.ui.comboBox_3.currentText()))
                    self.ui.listWidget_3.addItems(shape_list)
                else:
                    DataAnalysis.error_message("Selected Collection is not available")
        except Exception as e:
            DataAnalysis.error_message(str(e))

    def shape_attribute(self):
        try:
            checkbox_status = bool(self.ui.checkBox.isChecked())
            checkbox2_status = bool(self.ui.checkBox_2.isChecked())
            self.selected_shape_list = DataAnalysis.qt_object_to_list(self.ui.listWidget_3.selectedItems())
            self.ui.tableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem(",".join(self.selected_shape_list)))
            self.ui.tableWidget.show()
            self.ui.listWidget_2.clear()
            self.ui.label_5.clear()
            self.ui.tableWidget_3.setItem(0, 0, QtWidgets.QTableWidgetItem(""))
            self.ui.tableWidget_3.setItem(0, 1, QtWidgets.QTableWidgetItem(""))
            self.ui.tableWidget_3.setItem(0, 2, QtWidgets.QTableWidgetItem(""))
            self.ui.label_6.clear()
            self.ui.listWidget.clear()
            self.ui.tableWidget.setItem(0, 3, QtWidgets.QTableWidgetItem(""))
            self.ui.tableWidget.setItem(0, 4, QtWidgets.QTableWidgetItem(""))
            self.ui.tableWidget_2.setItem(1, -1, QtWidgets.QTableWidgetItem(""))
            if len(self.selected_shape_list) != 0:
                if checkbox_status is True and checkbox2_status is False:
                    sign_list = self.data_processing.execute_query("sign", str(self.ui.comboBox_3.currentText()),
                                                                    {"class": self.selected_shape_list,
                                                                    "image": ["1"]})
                    self.ui.listWidget_2.addItems(sign_list)
                elif checkbox_status is False and checkbox2_status is True:
                    sign_list = self.data_processing.execute_query("sign", str(self.ui.comboBox_3.currentText()),
                                                                {"class": self.selected_shape_list,
                                                                "image": ["0"]})
                    self.ui.listWidget_2.addItems(sign_list)
                elif checkbox_status is True and checkbox2_status is True:
                    sign_list = self.data_processing.execute_query("sign", str(self.ui.comboBox_3.currentText()),
                                                               {"class": self.selected_shape_list})
                    self.ui.listWidget_2.addItems(sign_list)
            else:
                self.ui.listWidget_2.clear()
                self.ui.listWidget.clear()
                self.ui.tableWidget.setItem(0, 3, QtWidgets.QTableWidgetItem(""))
                self.ui.tableWidget.setItem(0, 4, QtWidgets.QTableWidgetItem(""))
                self.ui.tableWidget_2.setItem(1, -1, QtWidgets.QTableWidgetItem(""))
                self.ui.tableWidget.show()
                self.ui.label_5.clear()
        except Exception as e:
            DataAnalysis.error_message(str(e))

    def sign_attribute(self):
        try:
            self.selected_sign_list = DataAnalysis.qt_object_to_list(self.ui.listWidget_2.selectedItems())
            self.ui.tableWidget.setItem(0, 3, QtWidgets.QTableWidgetItem(",".join(self.selected_sign_list)))
            self.ui.tableWidget.show()
            self.ui.tableWidget.resizeColumnsToContents()
            self.ui.listWidget.clear()
            self.ui.tableWidget_3.setItem(0, 0, QtWidgets.QTableWidgetItem(""))
            self.ui.tableWidget_3.setItem(0, 1, QtWidgets.QTableWidgetItem(""))
            self.ui.tableWidget_3.setItem(0, 2, QtWidgets.QTableWidgetItem(""))
            self.ui.label_6.clear()
            if(len(self.selected_sign_list)) != 0:
                country_list = self.data_processing.execute_query("country", str(self.ui.comboBox_3.currentText()),
                                                                {"class": self.selected_shape_list,
                                                                "sign": self.selected_sign_list})
                self.ui.listWidget.addItems(country_list)
                self.load_signs(self.selected_sign_list[-1])
            else:
                self.ui.tableWidget.setItem(0, 4, QtWidgets.QTableWidgetItem(""))
                self.ui.tableWidget.show()
                self.ui.label_5.clear()
        except Exception as e:
            DataAnalysis.error_message(str(e))

    def country_attribute(self):
        self.selected_country_list = DataAnalysis.qt_object_to_list(self.ui.listWidget.selectedItems())
        self.ui.tableWidget.setItem(0, 4, QtWidgets.QTableWidgetItem(r",".join(self.selected_country_list)))
        self.ui.tableWidget.show()
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget_3.setItem(0, 0, QtWidgets.QTableWidgetItem(""))
        self.ui.tableWidget_3.setItem(0, 1, QtWidgets.QTableWidgetItem(""))
        self.ui.tableWidget_3.setItem(0, 2, QtWidgets.QTableWidgetItem(""))
        self.ui.label_6.clear()

    @staticmethod
    def qt_object_to_list(qt_object):
        selected_list = []
        for i in range(len(qt_object)):
            selected_list.append(str(qt_object[i].text()))
        return selected_list

    def profile(self):
        self.ui.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem(str(self.ui.comboBox_7.currentText())))
        self.ui.tableWidget.show()

    def load_signs(self, sign_name):
        self.ui.label_5.clear()
        image_path = os.path.join(os.getcwd(), "Sign_images", str(sign_name + ".png"))
        pixmap = QtGui.QPixmap(QtGui.QImageReader(image_path).read())
        pixmap.scaledToWidth(self.ui.label_5.width())
        pixmap.scaledToHeight(self.ui.label_5.height())
        self.ui.label_5.setScaledContents(True)
        self.ui.label_5.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.ui.label_5.setPixmap(pixmap)

    def sign_count(self):
        try:
            if len(self.selected_country_list) == 0 or len(self.selected_sign_list) == 0:
                DataAnalysis.error_message("Please select Sign ID and Country ID")
            else:
                sign_list = self.data_processing.execute_query("sign", str(self.ui.comboBox_3.currentText()),
                                                  {'country': self.selected_country_list,
                                                   'sign': self.selected_sign_list}, False)
                self.ui.tableWidget_2.setItem(1, -1, QtWidgets.QTableWidgetItem(str(len(sign_list))))
                self.ui.tableWidget_2.show()
        except Exception as e:
            DataAnalysis.error_message(str(e))

    def plot(self, output_format="Bar_graph", pop_up=False):
        try:
            parameters = {
                "Histogram Height": "height",
                "Histogram Width": "width",
                "Scale Height": "x_scale",
                "Scale Width": "y_scale",
                "Aspect Ratio": "aspectratio"
                }
            if self.ui.comboBox_7.currentText() == 0 or self.selected_sign_list is None or \
                    self.selected_shape_list is None or self.selected_country_list is None:
                DataAnalysis.error_message("Please select Profile, Shape, Sign ID and Country ID first")

            else:
                column_name = parameters[str(self.ui.comboBox_7.currentText())]
                param_dict = {}
                if len(self.selected_sign_list) != 0:
                    param_dict.update({"sign": self.selected_sign_list})
                if len(self.selected_shape_list) != 0:
                    param_dict.update({"class": self.selected_shape_list})
                if len(self.selected_country_list) != 0:
                    param_dict.update({"country": self.selected_country_list})
                if output_format == "Bar_graph":
                    min_bin = self.ui.tableWidget_3.item(0, 0).text()
                    max_bin = self.ui.tableWidget_3.item(0, 1).text()
                    bin_size = self.ui.tableWidget_3.item(0, 2).text()
                    bin_list = self.data_processing.hist_list(column_name, str(self.ui.comboBox_3.currentText()),
                                                              param_dict, False, [min_bin, max_bin, bin_size],
                                                              str(self.ui.comboBox_7.currentText()))
                    self.ui.tableWidget_3.setItem(0, 0, QtWidgets.QTableWidgetItem(str(bin_list[0])))
                    self.ui.tableWidget_3.show()
                    self.ui.tableWidget_3.setItem(0, 1, QtWidgets.QTableWidgetItem(str(bin_list[1])))
                    self.ui.tableWidget_3.show()
                    self.ui.tableWidget_3.setItem(0, 2, QtWidgets.QTableWidgetItem(str(bin_list[2])))
                    self.ui.tableWidget_3.show()
                    self.ui.label_6.clear()
                    pixmap = QtGui.QPixmap(QtGui.QImageReader(str(self.ui.comboBox_3.currentText()) + ".png").read())
                    pixmap.scaledToWidth(self.ui.label_6.width())
                    pixmap.scaledToHeight(self.ui.label_6.height())
                    self.ui.label_6.setScaledContents(True)
                    self.ui.label_6.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
                    self.ui.label_6.setPixmap(pixmap)
                    os.remove(str(self.ui.comboBox_3.currentText()) + ".png")
                else:
                    output_list = self.data_processing.execute_query(column_name,
                                                                     str(self.ui.comboBox_3.currentText()),
                                                                     param_dict, False)
                    profile_dict = {i: output_list.count(i) for i in set(output_list)}
                    pd.DataFrame({column_name: list(profile_dict.keys()),
                                  "Image_Frequency ": list(profile_dict.values())}).\
                        to_csv(str(self.ui.comboBox_3.currentText())+".csv", index=False)
                    pd.DataFrame({column_name: output_list}).to_csv(str(self.ui.comboBox_3.currentText())
                                                                    + "_raw"+".csv", index=False)

            if pop_up is True:
                print("In the pop-up")
                self.data_processing.plt_object.show()

        except Exception as e:
            DataAnalysis.error_message((str(e)))

    def export_csv(self):
        self.plot("export_to_csv")

    def reset_bin_table(self):
        self.ui.tableWidget_3.setItem(0, 0, QtWidgets.QTableWidgetItem(""))
        self.ui.tableWidget_3.setItem(0, 1, QtWidgets.QTableWidgetItem(""))
        self.ui.tableWidget_3.setItem(0, 2, QtWidgets.QTableWidgetItem(""))



