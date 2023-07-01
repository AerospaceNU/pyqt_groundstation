import asyncio
from math import floor
from queue import Queue
import time
from os.path import exists

import aiohttp
import cv2
import numpy
import os

from src.Modules.MapTileManager.tile_convert import bbox_to_xyz, tile_edges

CACHE_FOLDER = "tile_cache"
OFFLINE = False

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

def get_tile_from_offline_cache(x,y,zoom, tile_cache, new_tiles_queue: Queue, recursion_depth=0):
    subsampleIfInCache: bool = True
    max_recursion=5   

    tile_name = get_tile_name(x, y, zoom)

    # Simple case: tile exists in cache
    if tile_name in tile_cache:
        print("Cache hit")
        return (tile_cache[tile_name], recursion_depth)

    # Next simplest case: tile exists on disk, but not yet in the dict. Add it to the queue
    if exists(get_file_path(x, y, zoom)):
        imread_start = time.time()
        ret = cv2.imread(get_file_path(x, y, zoom), cv2.IMREAD_UNCHANGED)
        imread_end = time.time()
        print(f"Loaded from disk in {(imread_end - imread_start) * 1e3} ms")
        
        # memoize the tile we loaded from disk for later. Non-multithreaded code will update the cache
        new_tiles_queue.put((tile_name, ret))

        return (ret, recursion_depth)

    # Give up if we shouldn't try tomfoolery
    if not subsampleIfInCache or recursion_depth > max_recursion:
        # print(f"{x}:{y}:{zoom}: Reached max recursion!")
        return (None, recursion_depth)

    # Tile name of the next-zoom-level-up tile that contains the same info
    parent_x = floor(x/2.0)
    parent_y = floor(y/2.0)
    parent_z = zoom - 1
    parent_img, parent_depth = get_tile_from_offline_cache(parent_x, parent_y, parent_z, tile_cache, new_tiles_queue, recursion_depth+1)

    if parent_img is None:
        # print(f"{x}:{y}:{zoom}: Recursive search failed, passing up None!")
        return (None, recursion_depth)

    # print(f"{x}:{y}:{zoom}: superscaling!")

    # we need to figure out which quadrant of the image we're in
    is_left_half = abs(y/2 % 1) < 1e-3
    is_top_half = abs(x/2 % 1) < 1e-3

    if is_left_half:
        x_min = 0
    else:
        x_min = 128

    if is_top_half:
        y_min = 0
    else:
        y_min = 128

    # print(f"Supersampling from x {x_min} and y {y_min}")

    IMAGE_SIZE = (256, 256)
    img = cv2.resize(parent_img[x_min:x_min+128, y_min:y_min+128], IMAGE_SIZE, interpolation=cv2.INTER_NEAREST)

    return (img, parent_depth)


async def download_task(tile_dict, tile_name, save_local_copy, x, y, z, queue, current_cache: dict):
    start_time = time.time()

    # If we're online but have the tile already saved, use it
    if exists(get_file_path(x, y, z)) and not OFFLINE:
        tile = cv2.imread(get_file_path(x, y, z), cv2.IMREAD_UNCHANGED)
    elif OFFLINE:
        # Use tile cache folder, and fake missing tiles using their cropped parents if we have to
        tile, recusion_depth = get_tile_from_offline_cache(x,y,z, current_cache, queue)
        if tile is None:
            return
        tile_is_fake = (recusion_depth < 1)
        tile_on_disk = tile_is_fake
    else:
        # Normal download from the interwebz
        data = []
        await download_tile(data, x, y, z)
        nparr = numpy.frombuffer(data[0], numpy.uint8)
        tile = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        tile_is_fake = False
        tile_on_disk = False


    if save_local_copy and not tile_is_fake and not tile_on_disk:
        # print("saving " + tile_name)
        cv2.imwrite(get_file_path(x, y, z), tile)

    tile_dict[tile_name] = tile

    end_time = time.time()
    # print(f"Download for {x} {y} {z} done in {(end_time - start_time) * 1e3} ms")


def get_bounding_box_tiles(lower_left, upper_right, zoom):
    lat_min = lower_left[0]
    lon_min = lower_left[1]
    lat_max = upper_right[0]
    lon_max = upper_right[1]

    return bbox_to_xyz(lon_min, lon_max, lat_min, lat_max, zoom)


def get_tile_name(x, y, zoom):
    return "{0},{1},{2}".format(zoom, x, y)


def get_file_path(x, y, zoom):
    return "{}/{}.png".format(CACHE_FOLDER, get_tile_name(x, y, zoom))


async def addAsyncTasks(bounding_box, zoom, exclude_list, save_local_copy, out_dict, current_tile_cache):
    [x_min, x_max, y_min, y_max] = bounding_box

    tasks = []
    queue = Queue(0)

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            tile_name = get_tile_name(x, y, zoom)

            if tile_name not in exclude_list:
                task = asyncio.create_task(download_task(out_dict, tile_name, save_local_copy, x, y, zoom, queue, current_tile_cache))
                tasks.append(task)
                # await task

    for task in tasks:
        await task

    while queue.qsize() > 0:
        try:
            (name, tile) = queue.get_nowait()
            out_dict[name] = tile
        except Exception as e:
            print(e)
            break


def get_all_tiles_in_box(bounding_box, zoom, current_cache, exclude_list=None, save_local_copy=False):
    if exclude_list is None or save_local_copy:
        exclude_list = []

    if save_local_copy and not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)

    out_dict = {}

    asyncio.run(addAsyncTasks(bounding_box, zoom, exclude_list, save_local_copy, out_dict, current_cache))

    return out_dict


def get_tiles_at_all_zoom_levels(lower_left_lla, upper_right_lla, save_local_copy=False):
    time.sleep(0.01)

    for i in range(10, 20):
        tile_set = get_bounding_box_tiles(lower_left_lla, upper_right_lla, i)
        get_all_tiles_in_box(tile_set, i, save_local_copy=save_local_copy)


def stitch_all_tiles_in_box(bounding_box, zoom, tile_database):
    [x_min, x_max, y_min, y_max] = bounding_box

    out_img = None

    # We know ahead of time how big the image should be, so pre-allocate it instead of concating as we go
    # in map land, x corrosponds to image columns and y to image rows
    out_img = numpy.zeros((256*(y_max-y_min+1), 256*(x_max-x_min+1), 3), dtype=numpy.uint8)

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            tile_name = get_tile_name(x, y, zoom)
            if tile_name in tile_database:
                tile = tile_database[tile_name]

                # Location of the top-left corner of the tile in our map, in pixels
                tile_start_col_px = (x-x_min)*256
                tile_start_row_px = (y-y_min)*256

                # Splice it into the image
                try:
                    out_img[tile_start_row_px:tile_start_row_px+256, tile_start_col_px:tile_start_col_px+256] = tile
                except Exception as e:
                    print(e)

            else:
                # tile isn't in our database. It's already black in the image, so we can just ignore
                pass

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
    zoom = 19
    tile_cache = {}
    tile_set = (int(23363*4), int(23363*4+10), int(50907*4), int(50907*4+10))

    for _ in range(5):

        start_time = time.time()
        tile_cache.update(get_all_tiles_in_box(tile_set, zoom, exclude_list=tile_cache.keys(), save_local_copy=False))
        end_time = time.time()

        print(f"Got {len(tile_cache)} tiles in {(end_time - start_time) * 1e3} ms")
        map_image = stitch_all_tiles_in_box(tile_set, zoom, tile_cache)

        cv2.imshow("map", cv2.resize(map_image, (1080, 720)))
        cv2.waitKey()
        cv2.destroyAllWindows()

