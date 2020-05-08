import sqlite3
import math
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd


class DataProcessing(object):

    def __init__(self):
        self.collection_name = None
        self.sqlite_db_connection = None
        self.sqlite_db_cursor = None
        self.plt_object = plt

    def get_cursor_for_sqlite(self, collection):
        self.collection_name = collection
        self.sqlite_db_connection = sqlite3.connect(self.collection_name)
        self.sqlite_db_cursor = self.sqlite_db_connection.cursor()

    @staticmethod
    def get_query(column_name, collection, condition_dictionary):
        if condition_dictionary is None:
            query_string = "SELECT " + column_name + " FROM " + collection
            return query_string
        else:
            query_string = "SELECT " + column_name + " FROM " + collection + " WHERE "
            for key in condition_dictionary:
                inner_query = ""
                for inner_key in condition_dictionary[key]:
                    inner_query = inner_query + key + "=" + "'" + inner_key + "'" + " OR "
                inner_query = "(" + inner_query.rstrip(" OR ") + ")" + " AND "
                query_string = query_string + inner_query
            return query_string.rstrip(" AND ")

    @staticmethod
    def get_bins(bin_number):
        if isinstance(bin_number, int):
            return int(bin_number)
        else:
            return float(bin_number)

    def execute_query(self, column_name, collection, condition_dictionary=None, filtered=True):
        self.get_cursor_for_sqlite(collection)
        height_list = []
        width_list = []
        if column_name == "aspectratio":
            height_output = self.sqlite_db_cursor.execute(DataProcessing.get_query("height", collection, condition_dictionary))
            for height in list(height_output):
                height_list.append(height[0])
            width_output = self.sqlite_db_cursor.execute(DataProcessing.get_query("width", collection, condition_dictionary))
            for width in list(width_output):
                width_list.append(width[0])
            x = pd.DataFrame(width_list)
            y = pd.DataFrame(height_list)
            aspect_ratio = x/y
            return aspect_ratio[0].tolist()
        elif column_name == "x_scale":
            x_scale = 1176.0
            width_output = self.sqlite_db_cursor.execute(DataProcessing.get_query("width", collection, condition_dictionary))
            for width in list(width_output):
                width_list.append(width[0])
            width_frame = pd.DataFrame(width_list)/x_scale
            return width_frame[0].tolist()
        elif column_name == "y_scale":
            y_scale = 640.0
            height_output = self.sqlite_db_cursor.execute(DataProcessing.get_query("height", collection, condition_dictionary))
            for height in list(height_output):
                height_list.append(height[0])
            height_frame = pd.DataFrame(height_list)/y_scale
            return height_frame[0].tolist()
        else:
            query_output = self.sqlite_db_cursor.execute(DataProcessing.get_query(column_name, collection, condition_dictionary))
            query_output_list = []
            if filtered is True:
                output = set(list(query_output))
            else:
                output = list(query_output)
            for shape in output:
                query_output_list.append(shape[0])
            return query_output_list

    def hist_list(self, column_name, collection, condition_dictionary, filtered=False, hist_bin=None,
                  profile_name = None):
        plt.clf()
        output_list = self.execute_query(column_name, collection, condition_dictionary, filtered)
        if hist_bin[0] == "" and hist_bin[1] == "" and hist_bin[2] == "":
            bin = ((max(output_list) + 1) - (min(output_list))) / math.sqrt(len(output_list))
            bins = np.arange(min(output_list), max(output_list), DataProcessing.get_bins(bin))
            hist_bin[0] = min(output_list)
            hist_bin[1] = max(output_list)
            hist_bin[2] = bin
        else:
            bins = np.arange(DataProcessing.get_bins(hist_bin[0]), DataProcessing.get_bins(hist_bin[1]),
                             DataProcessing.get_bins(hist_bin[2]))
        plt.title(collection)
        plt.xlabel(profile_name)
        y_label = "Frequency of Images"
        plt.ylabel(y_label)
        plt.xlim([DataProcessing.get_bins(hist_bin[0]), DataProcessing.get_bins(hist_bin[1])])
        plt.xticks(bins)
        plt.hist(output_list)
        plt.savefig(collection + ".png")
        plt.grid(True)
        return hist_bin


