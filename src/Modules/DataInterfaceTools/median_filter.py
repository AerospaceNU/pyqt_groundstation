"""
Single datapoint median filter
"""

import statistics
import time

import navpy

from src.data_helpers import vector_length


class MedianFilter(object):
    def __init__(self, filter_history_length=5):
        self.filter_history_length = filter_history_length
        self.data_list = []

    def new_data(self, new_data_point):
        self.data_list = (self.data_list + [new_data_point])[
            -self.filter_history_length :
        ]  # Put lat and lon in a list for median filter

    def get_filtered_data_output(self):
        if self.has_data():
            return statistics.median(self.data_list)
        else:
            return 0

    def has_data(self):
        return len(self.data_list) > 0

    def reset_filter(self):
        self.data_list = []
