import asyncio
import time
from os.path import exists

import aiohttp
import cv2
import numpy

from src.Modules.MapTileManager.tile_convert import bbox_to_xyz, tile_edges


async def download_tile(buf, x, y, z):
    # url = "https://a.tile.openstreetmap.org/{0}/{1}/{2}.png".format(z, x, y)
    url = "http://mt1.google.com/vt/lyrs=y&x={0}&y={1}&z={2}".format(x, y, z)

    # header_text = {
    #     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    #     "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    #     "Accept-Encoding": "none",
    #     "Accept-Language": "en-US,en;q=0.8",
    #     "Connection": "keep-alive",
    # }

    # request = Request(url, headers=header_text)
    # data = urllib.request.urlopen(request).read()

    semaphore = asyncio.BoundedSemaphore(50)  # I think this keeps too many from running at the same time

    async with semaphore, aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            assert resp.status == 200
            data = await resp.read()

    buf.append(data)


async def download_task(tile_dict, tile_name, save_local_copy, x, y, z):
    if exists(get_file_path(x, y, z)):
        tile = cv2.imread(get_file_path(x, y, z), cv2.IMREAD_UNCHANGED)
    else:
        data = []
        await download_tile(data, x, y, z)
        nparr = numpy.frombuffer(data[0], numpy.uint8)
        tile = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # print(tile_name)

    if save_local_copy:
        print("saving " + tile_name)
        cv2.imwrite(get_file_path(x, y, z), tile)

    tile_dict[tile_name] = tile


def get_bounding_box_tiles(lower_left, upper_right, zoom):
    lat_min = lower_left[0]
    lon_min = lower_left[1]
    lat_max = upper_right[0]
    lon_max = upper_right[1]

    return bbox_to_xyz(lon_min, lon_max, lat_min, lat_max, zoom)


def get_tile_name(x, y, zoom):
    return "{0},{1},{2}".format(zoom, x, y)


def get_file_path(x, y, zoom):
    return "tile_cache/{}.png".format(get_tile_name(x, y, zoom))


async def addAsyncTasks(bounding_box, zoom, exclude_list, save_local_copy, out_dict):
    [x_min, x_max, y_min, y_max] = bounding_box

    tasks = []

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            tile_name = get_tile_name(x, y, zoom)

            if tile_name not in exclude_list:
                task = asyncio.create_task(download_task(out_dict, tile_name, save_local_copy, x, y, zoom))
                tasks.append(task)
                # await task

    for task in tasks:
        await task


def get_all_tiles_in_box(bounding_box, zoom, exclude_list=None, save_local_copy=False):
    if exclude_list is None or save_local_copy:
        exclude_list = []

    out_dict = {}

    asyncio.run(addAsyncTasks(bounding_box, zoom, exclude_list, save_local_copy, out_dict))

    return out_dict


def get_tiles_at_all_zoom_levels(lower_left_lla, upper_right_lla, save_local_copy=False):
    time.sleep(0.1)

    for i in range(10, 20):
        tile_set = get_bounding_box_tiles(lower_left_lla, upper_right_lla, i)
        get_all_tiles_in_box(tile_set, i, save_local_copy=save_local_copy)


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


if __name__ == "__main__":
    start_time = time.time()
    tiles = get_all_tiles_in_box((158654, 158659, 193914, 193918), 19)
    end_time = time.time()

    print(f"Got {len(tiles)} tiles in {end_time - start_time} seconds")
