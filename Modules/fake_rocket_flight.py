import time
import math
import random
import navpy

from constants import Constants

from Modules.fcb_data_interface_core import FCBDataInterfaceCore

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
        self.ground_speed_scale = 0.1
        self.boost_accel = 98
        self.gravity = -9.8
        self.main_deploy_accel = 50
        self.drogue_speed = -50
        self.main_speed = -5
        self.boost_duration = 2

        # Fixed parameters and flight variables
        self.initial_latitude = 37.2431
        self.initial_longitude = -115.7930
        self.latitude = self.initial_latitude
        self.longitude = self.initial_longitude
        self.altitude = 0
        self.vertical_velocity = 0

        # State control
        self.state = 0
        self.last_loop_time = time.time()
        self.launch_time = 0

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
            self.distance_traveled = 0
            self.altitude = 0
            self.vertical_velocity = 0
            self.latitude = self.initial_latitude
            self.longitude = self.initial_longitude

            measured_acceleration = -self.gravity
            fcb_state = Constants.PREFLIGHT_STATE_INDEX  # Pre flight

            countdown_time = int(self.launch_time - time.time()) + 1
            self.logToConsoleThrottle("Launching in {}".format(countdown_time), 1, 1)

            if time.time() > self.launch_time:
                self.launch_time = time.time()
                self.state = BOOST
                self.logToConsole("Launching", 1)
        elif self.state == BOOST:
            self.vertical_velocity += self.boost_accel * loop_time
            measured_acceleration = self.boost_accel - self.gravity
            fcb_state = Constants.POWERED_ASCENT_STATE_INDEX

            if time.time() - self.launch_time > self.boost_duration:
                self.state = COAST
                self.logToConsole("Burnout", 1)
        elif self.state == COAST:
            self.vertical_velocity += self.gravity * loop_time
            measured_acceleration = 0
            fcb_state = Constants.COAST_TO_APOGEE_INDEX

            if self.vertical_velocity < 0:
                self.state = DROGUE
                self.logToConsole("Apogee", 1)
        elif self.state == DROGUE:
            self.vertical_velocity = max(self.vertical_velocity + self.gravity * loop_time, self.drogue_speed)  # Clamp at drogue speed
            measured_acceleration = random.uniform(0, 9.8)
            fcb_state = Constants.DROGUE_DESCENT_INDEX

            self.course_enu += random.uniform(-.1, .1)

            if self.altitude < 100:
                self.state = MAIN
                self.logToConsole("Main deploy", 1)
        elif self.state == MAIN:
            self.vertical_velocity = min(self.vertical_velocity + self.main_deploy_accel * loop_time, self.main_speed)
            measured_acceleration = random.uniform(0, 9.8)
            fcb_state = Constants.MAIN_DESCENT_INDEX

            if self.altitude < 0:
                self.state = LANDED
                self.logToConsole("Landed", 1)
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
        packet[Constants.altitude_key] = self.altitude
        packet[Constants.vertical_speed_key] = self.vertical_velocity
        packet[Constants.acceleration_key] = measured_acceleration

        packet[Constants.ground_station_latitude_key] = self.initial_latitude
        packet[Constants.ground_station_longitude_key] = self.initial_longitude

        packet[Constants.fcb_state_key] = Constants.fcb_state_names[fcb_state]

        self.handleParsedData("Sim flight packet", packet)

        self.updateEveryLoop()
