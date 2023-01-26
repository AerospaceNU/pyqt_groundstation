"""
Handles loading and processing of map tiles
"""

import navpy

from src.Modules.MapTileManager.map_tile_tools import (
    get_all_tiles_in_box,
    get_bounding_box_tiles,
    get_edges_for_tile_set,
    get_tiles_at_all_zoom_levels,
    get_zoom_level_from_pixels_per_meter,
    stitch_all_tiles_in_box,
)


class MapTile(object):
    """Class that encapsulates the data for a map tile"""

    def __init__(self, map_image, bottom_left, upper_right, at_max_zoom):
        self.map_image = map_image
        self.lower_left = bottom_left
        self.upper_right = upper_right
        self.at_max_zoom = at_max_zoom


class MapTileManager(object):
    def __init__(self):
        self.next_request = []
        self.callback_list = []
        self.download_request = None

        self.last_tile_set = [0, 0, 0, 0]

        self.tile_cache = {}  # Probably not the most efficient way to do this

        self.last_rendered_tile = None
        self.last_zoom = 0
        self.has_new_map = False

    def hasNewMap(self):
        return self.has_new_map

    def peekNewestTile(self):
        return self.last_rendered_tile

    def getLastTile(self) -> MapTile:
        self.has_new_map = False
        return self.last_rendered_tile

    def process_requests(self):
        if self.download_request is not None:
            lower_left = self.download_request[0][0:2]
            upper_right = self.download_request[1][0:2]
            zoom = 19

            download = True
        elif len(self.next_request) != 0:
            # Break out data
            request = self.next_request.copy()
            self.next_request = []
            lower_left = request[0][0:2]
            upper_right = request[1][0:2]
            pixel_width = request[2]

            # Calculate meters per pixel and then zoom level
            meter_width = abs(navpy.lla2ned(lower_left[0], lower_left[1], 0, upper_right[0], upper_right[1], 0)[1])
            meters_per_pixel = float(meter_width) / float(pixel_width)
            zoom = get_zoom_level_from_pixels_per_meter(meters_per_pixel)

            download = False
        else:
            return

        # Add some padding
        new_lower_left = navpy.ned2lla([-100, -100, 0], lower_left[0], lower_left[1], 0)[0:2]
        new_upper_right = navpy.ned2lla([100, 100, 0], upper_right[0], upper_right[1], 0)[0:2]

        if download:
            self.download_request = None
            get_tiles_at_all_zoom_levels(new_lower_left, new_upper_right, save_local_copy=True)
            return

        tile_set = get_bounding_box_tiles(new_lower_left, new_upper_right, zoom)

        if self.last_tile_set == tile_set:  # If we're getting the same data again, skip it
            return
        self.tile_cache.update(get_all_tiles_in_box(tile_set, zoom, exclude_list=self.tile_cache.keys()))

        map_image = stitch_all_tiles_in_box(tile_set, zoom, self.tile_cache)
        edges = get_edges_for_tile_set(tile_set, zoom)

        self.last_rendered_tile = MapTile(map_image, edges[0], edges[1], zoom == 19)

        self.has_new_map = True
        self.last_tile_set = tile_set
        self.last_zoom = zoom

    def request_new_tile(self, lower_left_lla, upper_right_lla, pixel_width):
        self.next_request = [lower_left_lla, upper_right_lla, pixel_width]

    def request_tile_download(self, lower_left_lla, upper_right_lla):
        self.download_request = [lower_left_lla, upper_right_lla]
