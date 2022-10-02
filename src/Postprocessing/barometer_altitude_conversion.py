import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# csv = pd.read_csv("output/LDRS-beanboozler-l265-output-post.csv")
# easymini = pd.read_csv("output/beanboozler easymini 8069 LDRS L265.csv")
csv = pd.read_csv("D:\\Downloads\\Terp_II_Flight_4_TeleMega_Edited.csv")

gpsAltMsl = csv["altitude2"]
pressure_array = csv["pressure"] / 101325
time_array = csv["time"]

lapseRate = -6.5e-3
R_DRY_AIR = 287.053
G_ACCEL_EARTH = 9.80665

def pressure_to_alt(pressureAtm, tempRefK, pressureRefAtm, agl: bool = True):
    ret = ((tempRefK) / lapseRate) \
        * (pow(pressureAtm / pressureRefAtm, -R_DRY_AIR * lapseRate / G_ACCEL_EARTH) - 1)
    if agl:
        ret = ret - ret[0]
    return ret

GROUND_TEMP = 23.9 + 273.15
GROUND_PRESSURE = 99796.874 / 101325

baro_uncorrected = pressure_to_alt(pressure_array, 288.15, 1.0, agl=True)
baro_corrected = pressure_to_alt(pressure_array, GROUND_TEMP, 1, agl=True)
gpsAltAgl = gpsAltMsl - gpsAltMsl[0]

plt.figure()
plt.subplot(311)
plt.title(f"Corrected, uncorrected and GPS altitude, meters\nBase temp: {int(GROUND_TEMP-273.15)}C, Base pressure: {int(GROUND_PRESSURE * 101325)}Pa")
plt.plot(time_array, gpsAltAgl, label="GPS Alt, AGL, m")
plt.plot(time_array, baro_uncorrected, label="Standard Day model")
plt.plot(time_array, baro_corrected, label="Corrected model (true base pressure/temp)")
plt.subplot(312)
plt.plot(time_array, baro_corrected - baro_uncorrected, label="Delta, corrected to standard model, meters")
plt.subplot(313)
plt.plot(time_array, csv["hdop"], label="hdop")
plt.plot(time_array, csv["vdop"], label="vdop")

plt.legend()
plt.show()
