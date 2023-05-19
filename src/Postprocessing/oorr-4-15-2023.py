import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

lapseRate = -6.5e-3
R_DRY_AIR = 287.053
G_ACCEL_EARTH = 9.80665

csv = pd.read_csv("~/Downloads/2023-04-15-oorr-output-FCB-post.csv")
# csv = pd.read_csv("~/Downloads/2023-04-15-beanboozler-output-FCB-post.csv")
csv2 = csv.copy()
csv2["timestamp_ms"] -= csv2["timestamp_ms"][0]
csv2["timestamp_ms"] /= 1000
csv2 = csv2[csv2["timestamp_ms"] < 55]
csv2 = csv2[csv2["timestamp_ms"] > 25]


def pressure_to_alt(pressureAtm, tempRefK, pressureRefAtm, agl: bool = True):
    ret = ((tempRefK) / lapseRate) * (pow(pressureAtm / pressureRefAtm, -R_DRY_AIR * lapseRate / G_ACCEL_EARTH) - 1)
    if agl:
        ret = ret - ret.iloc[0]
    return ret


GROUND_TEMP = 20 + 273.15
PRESSURE_REF = 0.993872440167777
pressure_array = csv2["baro_pres_avg"]
baro_alt = pressure_to_alt(pressure_array, GROUND_TEMP, PRESSURE_REF)
csv2["baro_alt_avg"] = baro_alt


def rerun_kalman():
    x_hat = np.array([0, 0]).reshape((2, 1))
    K_steady = np.array([0.03407042, 0.03685564]).reshape((2, 1))
    last_time_ms = csv2["timestamp_ms"].iloc[0]
    out = []
    for idx, row in csv2.iterrows():
        if row["state"] == 3:
            u = np.array([[0]])
        else:
            u = np.array([[row["imu1_accel_y_real"]]])

        dt = row["timestamp_ms"] - last_time_ms
        dt /= 1000
        last_time_ms = row["timestamp_ms"]

        # predict
        x_hat[0] = x_hat[0] + x_hat[1] * dt + 0.5 * u[0] * dt * dt
        x_hat[1] = x_hat[1] + u[0] * dt

        # correct
        error = row["baro_alt_avg"] - x_hat[0]
        x_hat[0] = x_hat[0] + K_steady[0] * error
        x_hat[1] = x_hat[1] + K_steady[1] * error

        out.append(x_hat.T)
    out = np.array(out)
    print(out)

    # plt.figure()
    # plt.plot(csv2["timestamp_ms"], out[:,0])
    # plt.show()


# rerun_kalman()


def plot_altitude_residual():
    # Drop the first baro alt
    baro_alt2 = baro_alt.iloc[1:]

    pos_z2 = csv2["pos_z"].iloc[:-1]

    time = csv2["timestamp_ms"].iloc[:-1]

    plt.figure()
    plt.subplot(311)
    plt.plot(time, pos_z2, label="Kalman alt")
    plt.plot(time, baro_alt2, label="Baro alt")
    plt.legend()
    plt.subplot(312)
    # plt.plot(time, baro_alt2.to_numpy() - pos_z2.to_numpy(), label="Altitude residual, m")
    plt.plot(csv2["timestamp_ms"], csv2["vel_z"], label="Z vel, m/s")
    plt.legend()
    plt.subplot(313)
    # plt.plot(csv2["timestamp_ms"], csv2['acc_z'], label="Accel Z")
    plt.plot(csv2["timestamp_ms"], csv2["trigger_status"], label="Big Trig")

    # plt.figure()
    # # plt.plot(time, np.diff(csv2["timestamp_ms"]) * 1000, label="dt, ms")
    # plt.scatter(csv2["timestamp_ms"], csv2["timestamp_ms"] * 1000, label="dt, ms")
    # print(max(np.diff(csv2["timestamp_ms"]) * 1000))
    # plt.legend()
    plt.show()


plot_altitude_residual()
