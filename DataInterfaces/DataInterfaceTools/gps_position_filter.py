"""
Really rough filter for GPS data

It checks to see if the position received is within 10000 meters of the last gps point, and only accepts positions that are
"""

import statistics


class GPSPositionFilter(object):
    def __init__(self, name, filter_history_length=10):
        self.name = name

        self.has_initial_point = False
        self.filter_history_length = filter_history_length

        self.latitude_list = []
        self.longitude_list = []

    def new_gps_coords(self, latitude, longitude):
        """Really simple threshold rejection filter, only takes points within 10km of the last fix"""

        if latitude == 0 or longitude == 0:  # Don't update the filter on 0 data
            return

        self.has_initial_point = True

        self.latitude_list = (self.latitude_list + [latitude])[-self.filter_history_length:]
        self.longitude_list = (self.longitude_list + [longitude])[-self.filter_history_length:]

    def get_filtered_position_output(self):
        if len(self.latitude_list) > 0 and len(self.longitude_list) > 0:
            latitude = statistics.median(self.latitude_list)
            longitude = statistics.median(self.longitude_list)

            return [latitude, longitude]
        else:
            return [0, 0]

    def has_gps_data(self):
        return self.has_initial_point

    def reset_filter(self):
        print("{} GPS Filer resetting".format(self.name))
        self.has_initial_point = False
        self.latitude_list = []
        self.longitude_list = []
