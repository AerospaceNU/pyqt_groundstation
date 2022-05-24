"""
Really rough filter for GPS data

Has a median filter for GPS position
Calculates ground speed and median filters that as well
"""

import statistics
import time

import navpy

from src.data_helpers import vector_length


class GPSPositionFilter(object):
    def __init__(self, name, filter_history_length=10):
        self.name = name

        self.has_initial_point = False
        self.filter_history_length = filter_history_length

        self.latitude_list = []
        self.longitude_list = []
        self.ground_speed_list = []

        self.last_lat_lon = [0, 0]
        self.last_lat_lon_time = 0

    def new_gps_coords(self, latitude, longitude):
        if latitude == 0 or longitude == 0:  # Don't update the filter on 0 data
            return

        self.has_initial_point = True

        self.latitude_list = (self.latitude_list + [latitude])[-self.filter_history_length :]  # Put lat and lon in a list for median filter
        self.longitude_list = (self.longitude_list + [longitude])[-self.filter_history_length :]

        # Calculate ground speed based on lsat two messages
        ned = navpy.lla2ned(latitude, longitude, 0, self.last_lat_lon[0], self.last_lat_lon[1], 0)
        delta_time = time.time() - self.last_lat_lon_time
        distance_traveled = vector_length(ned[1], ned[0])
        ground_speed = float(distance_traveled) / float(delta_time)
        self.ground_speed_list = (self.ground_speed_list + [ground_speed])[-self.filter_history_length :]  # Put it in a list for the median filter

        self.last_lat_lon = [latitude, longitude]
        self.last_lat_lon_time = time.time()

    def get_filtered_position_output(self):
        if len(self.latitude_list) > 0 and len(self.longitude_list) > 0:
            latitude = statistics.median(self.latitude_list)
            longitude = statistics.median(self.longitude_list)

            return [latitude, longitude]
        else:
            return [0, 0]

    def get_filtered_speed_output(self):
        if len(self.ground_speed_list) > 0:
            return statistics.median(self.ground_speed_list)
        else:
            return 0

    def has_gps_data(self):
        return self.has_initial_point

    def reset_filter(self):
        print("{} GPS Filer resetting".format(self.name))
        self.has_initial_point = False
        self.latitude_list = []
        self.longitude_list = []
