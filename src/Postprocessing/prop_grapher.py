import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv("D:\\Documents\\GitHub\\pyqt_groundstation\\logs\\08-21-2022_06-45-15\\PROP_DATA_0.txt")

time = data["timeStamp"] * 1e-3
time = time - time[0]

plt.figure()

xlim = (14100, 14200)

plt.subplot(311)
plt.plot(time, data["loxTankDucer"], label="lox tank, psi")
plt.xlim(xlim)
plt.legend()
plt.axvline(14161.18777)

plt.subplot(312)
plt.plot(time, data["loxVenturi"], label="lox venturi, psi")
plt.plot(time, data["kerVenturi"], label="ker venturi, psi")
plt.xlim(xlim)
plt.legend()
plt.axvline(14161.18777)

plt.subplot(313)
plt.plot(time, data["loadCell"], label="load cell, lb")
plt.xlim(xlim)
plt.legend()
plt.axvline(14161.18777)

plt.figure()
plt.scatter(time, data["kerInletTC"], label="ker inlet")
plt.scatter(time, data["kerOutletTC"], label="ker outlet")
plt.scatter(time, data["plume1TC"], label="plume 1")
plt.scatter(time, data["plume2TC"], label="plume 2")
plt.scatter(time, data["throatTC"], label="Throat")
plt.legend()
plt.xlim(xlim)

plt.show()
