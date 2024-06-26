import logging
import math
import random
import time

import ahrs
import navpy
import numpy as np

from src.constants import Constants
from src.data_helpers import euler_to_quaternion, quaternion_to_euler_angle
from src.Modules.fcb_data_interface_core import FCBDataInterfaceCore

# Internal states for the physics state machine
PRE_FLIGHT = 0
BOOST = 1
COAST = 2
DROGUE = 3
MAIN = 4
LANDED = 5


class FakeFlight(FCBDataInterfaceCore):
    """
    Generates random data for testing
    """

    def __init__(self):
        super().__init__()

        # Rocket parameters
        self.course_enu = 1  # Initial course
        self.ground_speed_scale = 0.25
        self.boost_accel = 98
        self.gravity = -9.8
        self.main_deploy_accel = 50
        self.drogue_speed = -50
        self.main_speed = -5
        self.boost_duration = 1

        self.pyro_status = [False, False, False, False]

        # Fixed parameters and flight variables
        self.initial_latitude = 37.235900
        self.initial_longitude = -115.819586
        self.latitude = self.initial_latitude
        self.longitude = self.initial_longitude
        self.altitude = 0
        self.vertical_velocity = 0

        # State control
        self.state = 0
        self.last_loop_time = time.time()
        self.launch_time = 0

        quaternion_init = euler_to_quaternion(0, math.radians(90), 0)
        self.quaternion_wxyz = np.array(quaternion_init)
        self.filter = ahrs.filters.AngularRate()

    def runOnEnableAndDisable(self):
        if self.enabled:
            self.launch_time = time.time() + 5
            self.state = PRE_FLIGHT

    def spin(self):
        loop_time = time.time() - self.last_loop_time
        self.last_loop_time = time.time()

        self.good_fcb_data = True
        self.connected = True
        self.has_data = True
        self.good_radio_crc = True

        packet = {}

        if self.state == PRE_FLIGHT:
            self.altitude = 0
            self.vertical_velocity = 0
            self.latitude = self.initial_latitude
            self.longitude = self.initial_longitude

            measured_acceleration = -self.gravity
            fcb_state = Constants.PREFLIGHT_STATE_INDEX  # Pre flight

            countdown_time = int(self.launch_time - time.time()) + 1
            self.logToConsoleThrottle("Launching in {}".format(countdown_time), logging.DEBUG, 1)

            if time.time() > self.launch_time:
                self.launch_time = time.time()
                self.state = BOOST
                self.logger.info("Launching")
        elif self.state == BOOST:
            self.vertical_velocity += self.boost_accel * loop_time
            measured_acceleration = self.boost_accel - self.gravity
            fcb_state = Constants.POWERED_ASCENT_STATE_INDEX

            if time.time() - self.launch_time > self.boost_duration:
                self.state = COAST
                self.logger.info("Burnout")
        elif self.state == COAST:
            self.vertical_velocity += self.gravity * loop_time
            measured_acceleration = 0
            fcb_state = Constants.COAST_TO_APOGEE_INDEX

            if self.vertical_velocity < 0:
                self.state = DROGUE
                self.logger.info("Apogee")
        elif self.state == DROGUE:
            self.vertical_velocity = max(self.vertical_velocity + self.gravity * loop_time, self.drogue_speed)  # Clamp at drogue speed
            measured_acceleration = random.uniform(0, 9.8)
            fcb_state = Constants.DROGUE_DESCENT_INDEX

            self.course_enu += random.uniform(-0.1, 0.1)
            self.pyro_status[0] = True

            if self.altitude < 100:
                self.state = MAIN
                self.logger.info("Main deploy")
        elif self.state == MAIN:
            self.vertical_velocity = min(self.vertical_velocity + self.main_deploy_accel * loop_time, self.main_speed)
            measured_acceleration = random.uniform(0, 9.8)
            fcb_state = Constants.MAIN_DESCENT_INDEX
            self.pyro_status[2] = True

            if self.altitude < 0:
                self.state = LANDED
                self.logger.info("Landed")
        elif self.state == LANDED:
            measured_acceleration = -self.gravity
            self.altitude = 0
            self.vertical_velocity = 0
            fcb_state = Constants.END_STATE_INDEX
        else:
            fcb_state = Constants.UNKNOWN_STATE_INDEX
            measured_acceleration = 0

        self.altitude += self.vertical_velocity * loop_time
        ground_speed = self.vertical_velocity * self.ground_speed_scale
        distance_traveled = ground_speed * loop_time

        delta_x = distance_traveled * math.cos(self.course_enu)
        delta_y = distance_traveled * math.sin(self.course_enu)
        [self.latitude, self.longitude, _] = navpy.ned2lla([delta_y, delta_x, 0], self.latitude, self.longitude, 0)
        packet[Constants.latitude_key] = self.latitude
        packet[Constants.longitude_key] = self.longitude

        packet[Constants.backup_gps_latitude] = self.latitude - 0.000025
        packet[Constants.backup_gps_longitude] = self.longitude - 0.000025

        packet[Constants.altitude_key] = self.altitude
        packet[Constants.vertical_speed_key] = self.vertical_velocity
        packet[Constants.acceleration_key] = measured_acceleration
        packet[Constants.pyro_fire_status] = self.pyro_status

        packet[Constants.ground_station_latitude_key] = self.initial_latitude
        packet[Constants.ground_station_longitude_key] = self.initial_longitude

        packet[Constants.fcb_state_number_key] = fcb_state

        # janky quaternion
        packet[Constants.rotational_velocity_x_key] = self.vertical_velocity / 10.0
        self.quaternion_wxyz = self.filter.update(self.quaternion_wxyz, np.array([packet[Constants.rotational_velocity_x_key], 0, 0]))

        packet[Constants.orientation_quaternion_key] = self.quaternion_wxyz
        rpy = quaternion_to_euler_angle(self.quaternion_wxyz)

        packet[Constants.roll_position_key] = rpy[0]
        packet[Constants.pitch_position_key] = rpy[1]
        packet[Constants.yaw_position_key] = rpy[2]

        for cutter in [0, 1, 2]:
            light = 1000 if self.state >= DROGUE else 12
            light = light + random.randint(-5, 5)

            packet[Constants.makeLineCutterString(cutter, Constants.line_cutter_number_key)] = cutter
            packet[Constants.makeLineCutterString(cutter, Constants.battery_voltage_key)] = 3
            packet[Constants.makeLineCutterString(cutter, Constants.altitude_key)] = self.altitude
            packet[Constants.makeLineCutterString(cutter, Constants.line_cutter_state_key)] = fcb_state
            packet[Constants.makeLineCutterString(cutter, Constants.photoresistor_key)] = light
            packet[Constants.makeLineCutterString(cutter, Constants.photoresistor_threshold_key)] = 500
            packet[Constants.makeLineCutterString(cutter, Constants.line_cutter_cut_1)] = self.state < DROGUE or self.altitude > 500
            packet[Constants.makeLineCutterString(cutter, Constants.line_cutter_cut_2)] = self.state < DROGUE or self.altitude > 1000

        self.handleParsedData("Sim flight packet", packet)

        self.updateEveryEnabledLoop()
