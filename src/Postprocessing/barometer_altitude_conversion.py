import pandas as pd
from matplotlib import pyplot as plt

# csv = pd.read_csv("output/LDRS-beanboozler-l265-output-post.csv")
# easymini = pd.read_csv("output/beanboozler easymini 8069 LDRS L265.csv")

gpsAltMsl = []
pressure_array = []
time_array = []

lapseRate = -6.5e-3
R_DRY_AIR = 287.053
G_ACCEL_EARTH = 9.80665


def make_telemega():
    csv = pd.read_csv("D:\\Downloads\\Terp_II_Flight_4_TeleMega_Edited.csv")

    global gpsAltMsl, pressure_array, time_array, GROUND_TEMP, GROUND_PRESSURE
    gpsAltMsl = csv["altitude2"]
    pressure_array = csv["pressure"] / 101325
    time_array = csv["time"]

    GROUND_TEMP = 23.9 + 273.15
    GROUND_PRESSURE = 99796.874 / 101325


def make_fcb():
    # csv = pd.read_csv("D:\\Downloads\\beanboozler-4-24-2022-output-post.csv")
    csv = pd.read_csv("output/LDRS-beanboozler-l265-output-post.csv")

    global gpsAltMsl, pressure_array, time_array, GROUND_TEMP, GROUND_PRESSURE

    gpsAltMsl = csv["gps_alt"]
    pressure_array = csv["baro_pres_avg"]
    time_array = csv["timestamp_s"] / 1000

    GROUND_TEMP = 39 + 273.15
    GROUND_PRESSURE = pressure_array[0]


def pressure_to_alt(pressureAtm, tempRefK, pressureRefAtm, agl: bool = True):
    ret = ((tempRefK) / lapseRate) * (pow(pressureAtm / pressureRefAtm, -R_DRY_AIR * lapseRate / G_ACCEL_EARTH) - 1)
    if agl:
        ret = ret - ret[0]
    return ret


# ================================

make_fcb()

baro_uncorrected = pressure_to_alt(pressure_array, 288.15, 1.0, agl=True)
baro_corrected = pressure_to_alt(pressure_array, GROUND_TEMP, 1, agl=True)
gpsAltAgl = gpsAltMsl - gpsAltMsl[0]

plt.figure()
plt.subplot(211)
plt.title(f"Corrected, uncorrected and GPS altitude, meters\nBase temp: {int(GROUND_TEMP-273.15)}C, Base pressure: {int(GROUND_PRESSURE * 101325)}Pa")
plt.plot(time_array, gpsAltAgl, label="GPS Alt, AGL, m")
plt.plot(time_array, baro_uncorrected, label="Standard Day model")
plt.plot(time_array, baro_corrected, label="Corrected model (true base pressure/temp)")
plt.legend()
plt.subplot(212)
plt.plot(time_array, baro_corrected - baro_uncorrected, label="Delta, corrected to standard model, meters")
plt.legend()

plt.show()
