#!/usr/bin/env python3

"""
Simple NMEA GPS Driver
"""

import time
import pynmea2

from dataclasses import dataclass


@dataclass
class Satellite(object):
    number: int
    elevation: float
    azimuth: float
    snr: float
    in_use: float


def checkValue(value):
    if value == "":
        a = -1
    else:
        try:
            a = float(value)
        except:
            a = -1

    return a


def convertToFloat(value: str, default_val):
    try:
        return float(value)
    except:
        return default_val


class GPSDriver(object):
    def __init__(self, require_nmea_checksum=True):
        self.numSatellites = 0
        self.fixQuality = False
        self.lastDataTime = 0

        self.requireNMEAChecksum = require_nmea_checksum

        self.latitude = 0
        self.longitude = 0
        self.altitude = 0
        self.v_error = 0

        self.satellites = {}

        self.onFixCallback = None

    def setFixCallback(self, new_callback: callable):
        self.onFixCallback = new_callback

    def newBytes(self, raw_bytes: bytes):
        data = raw_bytes.decode('utf-8')

        if len(data) > 1 and data[0] == '$':
            self.newNMEAString(data)

    def newNMEAString(self, new_string: str):
        if new_string.strip() != "":
            self.parseNMEA(new_string.strip())

    def parseNMEA(self, data: str):
        try:
            data = data.strip()

            if self.requireNMEAChecksum:
                msg = pynmea2.parse(data)
            else:
                msg = pynmea2.parse(data.split("*")[0], check=False)
        except Exception as e:
            # print("Could not parse NMEA string: {}".format(data))
            # print(e)
            return

        # TODO: Parse more message types
        if type(msg) == pynmea2.types.talker.GGA:  # GGA is a fix
            if convertToFloat(msg.latitude, None) is not None:  # Check if we have a latitude field (currently used as a proxy for a fix)
                self.lastDataTime = time.time()  # Not sure if we should only update this when we get a fix

                self.altitude = convertToFloat(msg.altitude, 0)
                self.v_error = convertToFloat(msg.horizontal_dil, -1)
                self.latitude = convertToFloat(msg.latitude, 0)
                self.longitude = convertToFloat(msg.longitude, 0)
                self.numSatellites = int(msg.num_sats)
                self.fixQuality = msg.gps_qual

                self.runOnFix()
        elif type(msg) == pynmea2.types.talker.GSA:  # GSA is information about the satellites we can see
            visible_sats = [-1] * 12
            visible_sats[0] = int(checkValue(msg.sv_id01))
            visible_sats[1] = int(checkValue(msg.sv_id02))
            visible_sats[2] = int(checkValue(msg.sv_id03))
            visible_sats[3] = int(checkValue(msg.sv_id04))
            visible_sats[4] = int(checkValue(msg.sv_id05))
            visible_sats[5] = int(checkValue(msg.sv_id06))
            visible_sats[6] = int(checkValue(msg.sv_id07))
            visible_sats[7] = int(checkValue(msg.sv_id08))
            visible_sats[8] = int(checkValue(msg.sv_id09))
            visible_sats[9] = int(checkValue(msg.sv_id10))
            visible_sats[10] = int(checkValue(msg.sv_id11))
            visible_sats[11] = int(checkValue(msg.sv_id12))

            # TODO: I don't think this is the correct behavior
            for sat_num in self.satellites:
                if sat_num in visible_sats:
                    self.satellites[sat_num].in_use = True
                else:
                    self.satellites[sat_num].in_use = False
        elif type(msg) == pynmea2.types.talker.GSV:  # GSA is more information about the satellites we can see
            self.parseSVData(msg.sv_prn_num_1, msg.elevation_deg_1, msg.azimuth_1, msg.snr_1)
            self.parseSVData(msg.sv_prn_num_2, msg.elevation_deg_2, msg.azimuth_2, msg.snr_2)
            self.parseSVData(msg.sv_prn_num_3, msg.elevation_deg_3, msg.azimuth_3, msg.snr_3)
            self.parseSVData(msg.sv_prn_num_4, msg.elevation_deg_4, msg.azimuth_4, msg.snr_4)
        elif type(msg) == pynmea2.types.talker.VTG:  # RMC has velocity information
            pass
        elif type(msg) == pynmea2.types.talker.VTG:  # VTG has velocity and course information
            pass

    def parseSVData(self, num, el, az, snr):
        num = checkValue(num)
        el = checkValue(el)
        az = checkValue(az)
        snr = checkValue(snr)

        if num == -1:
            return

        if num not in self.satellites:
            self.satellites[num] = Satellite(number=num, elevation=el, azimuth=az, snr=snr, in_use=False)
        else:
            self.satellites[num].elevation = el
            self.satellites[num].azimuth = az
            self.satellites[num].snr = snr

    def runOnFix(self):
        if self.onFixCallback is not None:
            try:
                self.onFixCallback()
            except Exception as e:
                print(f"Unable to run fix callback: {e}")

    def getLatitude(self):
        return self.latitude

    def getLongitude(self):
        return self.longitude

    def getAltitude(self):
        return self.altitude

    def generateDiagnosticsPage(self):
        diagnostics_lines = [["Latitude", self.latitude],
                             ["Longitude", self.longitude],
                             ["Fix Quality", self.fixQuality],
                             # ["Timed out", self.dataTimedOut],
                             ["Satellites", self.numSatellites],
                             ]

        for sat in self.satellites.values():  # First show all the ones in use
            if sat.in_use:
                diagnostics_lines.append(["SV {}".format(int(sat.number)), "* snr:{0} el:{1} az:{2}".format(sat.snr, sat.elevation, sat.azimuth)])

        for sat in self.satellites.values():  # Then show all the ones not in use
            if not sat.in_use:
                diagnostics_lines.append(["SV {}".format(int(sat.number)), "snr:{0} el:{1} az:{2}".format(sat.snr, sat.elevation, sat.azimuth)])

        return diagnostics_lines
