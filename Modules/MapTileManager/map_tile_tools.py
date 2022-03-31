import time
import urllib.request

from urllib.request import Request

from Modules.MapTileManager.tile_convert import bbox_to_xyz, tile_edges


def download_tile(x, y, z):
    url = "https://a.tile.openstreetmap.org/{0}/{1}/{2}.png".format(z, x, y)

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


def download_everything_in_bounding_box(lower_left, upper_right, zoom):
    lat_min = lower_left[0]
    lon_min = lower_left[1]
    lat_max = upper_right[0]
    lon_max = upper_right[1]

    [x_min, x_max, y_min, y_max] = bbox_to_xyz(lon_min, lon_max, lat_min, lat_max, zoom)

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            download_and_save_tile(x, y, zoom)
            print(x, y)


if __name__ == '__main__':
    download_everything_in_bounding_box([42, -72], [43, -71], 7)
