import math

import matplotlib.pylab as plt
import numpy as np

from Modules.MessageParsing.fcb_message_parsing import parse_fcb_message

dictlist = []

for line in open("D:\\Downloads\\raw_data.txt"):
    try:
        line = line.split(" ")[1]
        line = eval(line)
        # print(line)
        # last byte is crc-lqi
        # crc_lqi = line[len(line) - 1]
        # crc = crc_lqi & 0b10000000
        # crc = 1 if crc else 0
        # print(crc)
        (success, dict_, type) = parse_fcb_message(line)
        # print(dict_)
        dictlist.append(dict_)
    except Exception:
        pass

arr = [
    (d["latitude"], d["longitude"], ([0, 1, 0] if d["crc"] == "Good" else [1, 0, 0]))
    for d in dictlist
    if "latitude" in d
]
arr = np.array(arr)
lat = arr[:, 0]
lon = arr[:, 1]
crc = arr[:, 2]

dist = [
    math.sqrt((x - 42.3522786) ** 2 + (y + 71.0894531) ** 2) for (x, y) in zip(lat, lon)
]
y = [0 for x in dist]

fig = plt.figure()

dist = np.array(dist)
dist[dist > 0.6] = 0.06

# plt.scatter(dist, y, c=crc)
plt.scatter(lon, lat, c=crc)
plt.ylim(-100, 100)
plt.xlim(-100, 100)
plt.figure()
plt.hist(dist)
plt.show()
