import time
import urllib.request
from urllib.request import Request

import cv2
import navpy
import numpy

from src.Modules.MapTileManager.tile_convert import bbox_to_xyz, tile_edges


def download_tile(x, y, z):
    # url = "https://a.tile.openstreetmap.org/{0}/{1}/{2}.png".format(z, x, y)
    url = "http://mt1.google.com/vt/lyrs=y&x={0}&y={1}&z={2}".format(x, y, z)

    header_text = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive",
    }

    request = Request(url, headers=header_text)

    return urllib.request.urlopen(request).read()


def download_and_save_tile(x, y, z):
    data = download_tile(x, y, z)

    f = open("{0}-{1}-{2}.png".format(z, x, y), "wb")
    f.write(data)
    f.close()


def download_tile_as_cv2(x, y, z):
    data = download_tile(x, y, z)

    nparr = numpy.frombuffer(data, numpy.uint8)
    cv2_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    return cv2_img


def get_bounding_box_tiles(lower_left, upper_right, zoom):
    lat_min = lower_left[0]
    lon_min = lower_left[1]
    lat_max = upper_right[0]
    lon_max = upper_right[1]

    return bbox_to_xyz(lon_min, lon_max, lat_min, lat_max, zoom)


def get_tile_name(x, y, zoom):
    return "{0},{1},{2}".format(zoom, x, y)


def get_all_tiles_in_box(bounding_box, zoom, exclude_list=None):
    if exclude_list is None:
        exclude_list = []

    [x_min, x_max, y_min, y_max] = bounding_box

    out_dict = {}

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            tile_name = get_tile_name(x, y, zoom)

            if tile_name not in exclude_list:
                tile = download_tile_as_cv2(x, y, zoom)
                out_dict[tile_name] = tile

                time.sleep(0.01)  # Space out url requests a bit

    return out_dict


def stitch_all_tiles_in_box(bounding_box, zoom, tile_database):
    [x_min, x_max, y_min, y_max] = bounding_box

    out_img = None

    for x in range(x_min, x_max + 1):
        column = None
        for y in range(y_min, y_max + 1):
            tile_name = get_tile_name(x, y, zoom)

            if tile_name in tile_database:
                tile = tile_database[tile_name]
            else:
                tile = numpy.zeros((256, 256, 3), dtype=numpy.uint8)

            if column is None:
                column = tile
            else:
                column = numpy.concatenate((column, tile), axis=0)

        if out_img is None:
            out_img = column
        else:
            out_img = numpy.concatenate((out_img, column), axis=1)

    return out_img


def get_edges_for_tile_set(tile_set, zoom):
    [x_min, x_max, y_min, y_max] = tile_set

    lower_left = []
    upper_right = []

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            edges = tile_edges(x, y, zoom)  # lon, lat, lon, lat, but not really clear what order

            max_lat = max(edges[1], edges[3])  # Find mins and maxes
            min_lat = min(edges[1], edges[3])
            max_lon = max(edges[0], edges[2])
            min_lon = min(edges[0], edges[2])

            if len(lower_left) == 0:
                lower_left = [min_lat, min_lon]
                upper_right = [max_lat, max_lon]
            else:
                lower_left[0] = min(lower_left[0], min_lat)  # Latitude
                lower_left[1] = min(lower_left[1], min_lon)
                upper_right[0] = max(upper_right[0], max_lat)
                upper_right[1] = max(upper_right[1], max_lon)

    return lower_left, upper_right


# https://wiki.openstreetmap.org/wiki/Zoom_levels
# These are the meters/pixel numbers on the equator.
# This won't be true anywhere else, but unless we operate REALLY far north, we won't notice
ZOOM_LEVELS = [
    156412,
    78206,
    39103,
    19551,
    9776,
    4888,
    2444,
    1222,
    610.984,
    305.492,
    152.746,
    76.373,
    38.187,
    19.093,
    9.547,
    4.773,
    2.387,
    1.193,
    0.596,
    0.298,
]


def get_zoom_level_from_pixels_per_meter(pixels_per_meter):
    for value in ZOOM_LEVELS:
        if value < pixels_per_meter:
            return ZOOM_LEVELS.index(value)

    return 19  # Otherwise we return the highest zoom
