"""
Really rough filter for GPS data

It checks to see if the position received is within 10000 meters of the last gps point, and only accepts positions that are
"""

import navpy

from data_helpers import vector_length


class GPSPositionFilter(object):
    def __init__(self):
        self.latitude = 0
        self.longitude = 0
        self.has_initial_point = False

    def new_gps_coords(self, latitude, longitude):
        """Really simple threshold rejection filter, only takes points within 10km of the last fix"""

        if latitude == 0 or longitude == 0:  # Don't update the filter on 0 data
            return

        # TODO: Write a better filter for gps data
        # TODO: if we get bad GPS data, we should probably ignore the whole packet (or at least everything after GPS)
        if self.has_initial_point:
            ned_delta = navpy.lla2ned(latitude, longitude, 0, self.latitude, self.longitude, 0)
            if (vector_length(ned_delta[0], ned_delta[1])) < 10000:
                self.latitude = latitude
                self.longitude = longitude
            else:
                print("GUI received GPS position too far from last: [{0}, {1}].  Ignoring".format(latitude, longitude))
        else:
            self.latitude = latitude
            self.longitude = longitude
            self.has_initial_point = True

    def get_filtered_position_output(self):
        return [self.latitude, self.longitude]

    def has_gps_data(self):
        return self.has_initial_point
