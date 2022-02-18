"""
Sends data to a android phone over bluetooth
"""

import threading
import math
import time
import pynmea2
from bluetooth import *

from constants import Constants
from data_helpers import get_value_from_dictionary, interpolate

from DataInterfaces.data_interface_core import DataInterfaceCore


def decimal_degrees_to_deg_min(decimal_degrees):
    whole_degrees = math.floor(abs(decimal_degrees))
    degree_parts = abs(decimal_degrees) - whole_degrees
    minutes = str(interpolate(degree_parts, 0, 1, 0, 60))

    if len(minutes.split(".")[0]) == 1:
        minutes = "0" + minutes

    return str(whole_degrees) + minutes


def format_lat_lon_for_nmea(latitude, longitude):
    if latitude >= 0:
        lat_sign = "N"
    else:
        lat_sign = "S"

    if longitude >= 0:
        lon_sign = "E"
    else:
        lon_sign = "W"

    return [decimal_degrees_to_deg_min(latitude), lat_sign, decimal_degrees_to_deg_min(longitude), lon_sign]


class AndroidPhoneBluetoothInterface(DataInterfaceCore):
    def __init__(self):
        super().__init__()

        self.server_sock = BluetoothSocket(RFCOMM)
        self.server_sock.bind(("", PORT_ANY))

        self.client_sock_list = []

        self.connection_thread = threading.Thread(target=self.advertise_bluetooth)
        self.connection_thread.setDaemon(True)  # Means the thread dies when the main thread exits
        self.connection_thread.start()

    def spin(self):
        try:
            latitude = get_value_from_dictionary(self.gui_full_data_dictionary, Constants.latitude_key, 0)
            longitude = get_value_from_dictionary(self.gui_full_data_dictionary, Constants.longitude_key, 0)
            altitude = get_value_from_dictionary(self.gui_full_data_dictionary, Constants.altitude_key, 0)
            message_age = get_value_from_dictionary(self.gui_full_data_dictionary, Constants.message_age_key, 0)
            time_str = time.strftime('%H%M%S')

            if latitude != 0 and longitude != 0 and message_age < 5:
                [lat_min, lat_sign, lon_min, lon_sign] = format_lat_lon_for_nmea(latitude, longitude)
                # time, lat, lon, fix quality, satellites, hdop, alt, alt_unit, height above wgs84, height unit, DGPS time, DGPS station
                msg = pynmea2.GGA('GP', 'GGA', (time_str, lat_min, lat_sign, lon_min, lon_sign, '1', '04', '2.6', str(altitude), 'M', '0', 'M', '', '0000'))
                self.send_bluetooth(str(msg))

            time.sleep(1)
        except Exception as e:
            pass

    def advertise_bluetooth(self):
        print("Starting Bluetooth")
        self.server_sock.listen(1)

        port = self.server_sock.getsockname()[1]

        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        advertise_service(self.server_sock, "TestServer", service_id=uuid, service_classes=[uuid, SERIAL_PORT_CLASS], profiles=[SERIAL_PORT_PROFILE])

        while self.should_be_running:
            if self.enabled:
                print("Waiting for connection on RFCOMM channel %d" % port)
                client_socket, client_info = self.server_sock.accept()
                self.client_sock_list.append(client_socket)
                print("Accepted connection from ", client_info)
            else:
                time.sleep(1)

    def send_bluetooth(self, dataString):
        dataString += "\n"
        for client_socket in self.client_sock_list:
            try:
                client_socket.send(dataString)
            except Exception as e:
                print("Lost bluetooth connection")
                client_socket.close()
                self.client_sock_list.remove(client_socket)
