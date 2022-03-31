"""
Handles loading and processing of map tiles
"""

from Modules.MapTileManager.map_tile_tools import download_everything_in_bounding_box


class MapTile(object):
    """Class that encapsulates the data for a map tile"""

    def __init__(self, map_image, bottom_left, upper_right):
        self.map_image = map_image
        self.bottom_left = bottom_left
        self.upper_right = upper_right


class MapTileManager(object):
    def __init__(self):
        self.request_queue = []

    def process_requests(self):
        if len(self.request_queue) == 0:
            return

        request = self.request_queue.pop()
        lower_left = request[0][0:2]
        upper_right = request[1][0:2]
        download_everything_in_bounding_box(lower_left, upper_right, 7)

    def request_new_tile(self, lower_left_lla, upper_right_lla):
        self.request_queue.append([lower_left_lla, upper_right_lla])
