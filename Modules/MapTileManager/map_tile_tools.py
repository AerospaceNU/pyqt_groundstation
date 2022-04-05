import cv2
import navpy
import numpy
import time
import urllib.request

from urllib.request import Request

from Modules.MapTileManager.tile_convert import bbox_to_xyz, tile_edges


def download_tile(x, y, z):
    # url = "https://a.tile.openstreetmap.org/{0}/{1}/{2}.png".format(z, x, y)
    url = "http://mt1.google.com/vt/lyrs=y&x={0}&y={1}&z={2}".format(x, y, z)

    header_text = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                   'Accept-Encoding': 'none',
                   'Accept-Language': 'en-US,en;q=0.8',
                   'Connection': 'keep-alive'}

    request = Request(url, headers=header_text)

    return urllib.request.urlopen(request).read()


def download_and_save_tile(x, y, z):
    data = download_tile(x, y, z)

    f = open('{0}-{1}-{2}.png'.format(z, x, y), 'wb')
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


def get_all_tiles_in_box(bounding_box, zoom):
    [x_min, x_max, y_min, y_max] = bounding_box

    out_img = None

    for x in range(x_min, x_max + 1):
        column = None
        for y in range(y_min, y_max + 1):
            tile = download_tile_as_cv2(x, y, zoom)
            time.sleep(0.01) # Space out url requests a bit

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


if __name__ == '__main__':
    zoom = 19

    origin = [42.3601, -71.0589]
    coords_2 = navpy.ned2lla([100, 200, 0], origin[0], origin[1], 0)[0:2]
    print(origin, coords_2)

    bbox = get_bounding_box_tiles(origin, coords_2, zoom)
    img = get_all_tiles_in_box(bbox, zoom)

    cv2.imshow("test", img)
    cv2.waitKey(0)
