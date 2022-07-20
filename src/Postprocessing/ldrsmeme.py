from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

csv = pd.read_csv("output/LDRS-beanboozler-l265-output-post.csv")
# csv = pd.read_csv("D:\\Downloads\\trd-4-2-22-output-post.csv")
easymini = pd.read_csv("output/beanboozler easymini 8069 LDRS L265.csv")
# easymini = pd.read_csv("D:\\Downloads\\2022-05-30-serial-8405-flight-0001.csv")

gpsAlt = csv["gps_alt"]

lapseRate = -0.0065;  # valid below 11000m, use lookup table for lapse
                            # rate when altitude is higher
tempRef = 15 + 273.15 #cliGetConfigs()->groundTemperatureC + 273.15;  # C to K
elevRef = 0 #cliGetConfigs()->groundElevationM;
presAvg = csv["baro_pres_avg"]#(curSensorVals->baro1_pres + curSensorVals->baro2_pres) / 2;
presRef = 1.0
GROUND_TEMP = 39.5
ALT_MSL = gpsAlt[0]
R_DRY_AIR =287.0474909  
G_ACCEL_EARTH =9.80665 
baroAlt = (tempRef / lapseRate) *\
                (1 - (presAvg / presRef) ** \
                            (R_DRY_AIR * lapseRate / G_ACCEL_EARTH)) +\
            elevRef

baroAlt = baroAlt - baroAlt[0]

t = csv["baro_temp_avg"][0]
print(f"Ground temp: {t} Msl: {ALT_MSL}")

# NAKKA compensation
newBaro = []
for b in baroAlt:
    out = b - b * (15 - GROUND_TEMP) / (273.15 + GROUND_TEMP + 0.5*(lapseRate)*(b + ALT_MSL))
    newBaro.append(out)

baroAltComp = np.array(newBaro)

if True:
    newBaro = []
    true = list(easymini["height"])
    for b in easymini["height"]:
        out = b - b * (15 - GROUND_TEMP) / (273.15 + GROUND_TEMP + 0.5*(lapseRate)*(b + ALT_MSL))
        newBaro.append(out)
    easymini["newheight"] = np.array(newBaro)

print(f"MAX alt: {max(newBaro)}")
csv["timestamp_s"] = csv["timestamp_s"] - csv["timestamp_s"][0] - 51
plt.figure()
# plt.subplot(211)
# plt.plot(csv["timestamp_s"], presAvg, label="FCB Baro pressure, Pa")
# plt.plot(easymini["time"], easymini["pressure"] / 101325, label="Easymini Baro pressure, Pa")
# plt.legend()
# plt.subplot(212)
plt.plot(csv["timestamp_s"], baroAlt, label="FCB Baro alt, AGL, m, temp=" + str(tempRef) + "deg K")
plt.plot(csv["timestamp_s"], baroAltComp, label="Compensated FCB Baro alt, AGL, m, temp=" + str(tempRef) + "deg K")
gpsAlt = gpsAlt - gpsAlt[0]
plt.plot(csv["timestamp_s"], gpsAlt,  label="FCB GPS Alt, AGL, m")
plt.plot(easymini["time"], easymini["newheight"], label="Easymini corrected, AGL, m")
plt.plot(easymini["time"], easymini["height"], label="Easymini uncorrected alt, m")
plt.legend()
plt.show()
