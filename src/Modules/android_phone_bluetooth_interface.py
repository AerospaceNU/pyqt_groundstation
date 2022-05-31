import math
import sys
import threading
import time

try:
    # If pybluez installation fails, this import won't work. Still allow GUI to run in that case
    import bluetooth.btcommon as ble
except ImportError:
    pass
import pynmea2

from src.constants import Constants
from src.data_helpers import get_value_from_dictionary, interpolate
from src.Modules.data_interface_core import ThreadedModuleCore


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

    return [
        decimal_degrees_to_deg_min(latitude),
        lat_sign,
        decimal_degrees_to_deg_min(longitude),
        lon_sign,
    ]


class AndroidPhoneBluetoothInterface(ThreadedModuleCore):
    """
    Sends data to a android phone over bluetooth
    """

    def __init__(self):
        super().__init__()
        self.server_sock = ble.BluetoothSocket(ble.RFCOMM)
        self.server_sock.bind(("", ble.PORT_ANY))
        self.server_sock.settimeout(1)
        self.bluetooth_running = False

        self.client_sock_list = []

        self.connection_thread = threading.Thread(target=self.advertise_bluetooth)
        self.connection_thread.setDaemon(True)  # Means the thread dies when the main thread exits
        self.connection_thread.start()

    def spin(self):
        """
        Creates a NMEA string of the vehicle position and sends that to all the connected clients at 1hz
        """

        try:
            latitude = get_value_from_dictionary(self.gui_full_data_dictionary, Constants.latitude_key, 0)
            longitude = get_value_from_dictionary(self.gui_full_data_dictionary, Constants.longitude_key, 0)
            altitude = get_value_from_dictionary(self.gui_full_data_dictionary, Constants.altitude_key, 0)
            message_age = get_value_from_dictionary(self.gui_full_data_dictionary, Constants.message_age_key, 0)
            time_str = time.strftime("%H%M%S")

            if latitude != 0 and longitude != 0 and message_age < 5:
                [lat_min, lat_sign, lon_min, lon_sign] = format_lat_lon_for_nmea(latitude, longitude)
                # time, lat, lon, fix quality, satellites, hdop, alt, alt_unit, height above wgs84, height unit, DGPS time, DGPS station
                msg = pynmea2.GGA(
                    "GP",
                    "GGA",
                    (
                        time_str,
                        lat_min,
                        lat_sign,
                        lon_min,
                        lon_sign,
                        "1",
                        "04",
                        "2.6",
                        str(altitude),
                        "M",
                        "0",
                        "M",
                        "",
                        "0000",
                    ),
                )
                self.send_bluetooth(str(msg))

            time.sleep(1)
        except Exception:
            pass

    def advertise_bluetooth(self):
        """
        Runs in a separate thread to handle new connections
        """

        time.sleep(1)  # wait for other stuff to spin up
        can_start = True

        # Try to set up the socket, and handle the errors that have come up in testing
        try:
            self.server_sock.listen(1)
            port = self.server_sock.getsockname()[1]
            uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
            ble.advertise_service(
                self.server_sock,
                "TestServer",
                service_id=uuid,
                service_classes=[uuid, ble.SERIAL_PORT_CLASS],
                profiles=[ble.SERIAL_PORT_PROFILE],
            )
            self.logToConsole("Starting Bluetooth", 1)
        except ble.BluetoothError as e:
            self.logToConsole("Can't start bluetooth: {}".format(e), 2)
            if "permission" in str(e).lower() and sys.platform == "linux":
                self.logToConsole(
                    "Linux permission error for bluetooth, try running [sudo chmod o+rw /var/run/sdp]",
                    2,
                )
            can_start = False

        # Wait for connections, and add them to the client list
        while self.should_be_running and can_start:
            if self.enabled and not self.bluetooth_running:
                self.logToConsole("Waiting for connection on RFCOMM channel {}".format(port), 0)
            if not self.enabled and self.bluetooth_running:
                self.logToConsole(
                    "No longer advertising bluetooth on channel {}".format(port),
                    1,
                    override_disabled_check=True,
                )

            if self.enabled:
                self.bluetooth_running = True
                try:
                    client_socket, client_info = self.server_sock.accept()
                    self.client_sock_list.append(client_socket)
                    self.logToConsole("Accepted connection from {}".format(client_info), 1)
                except ble.BluetoothError:
                    pass
            else:
                time.sleep(1)
                self.bluetooth_running = False

    def send_bluetooth(self, data_string):
        """
        Send dataString to every connected bluetooth client
        """

        data_string += "\n"
        for client_socket in self.client_sock_list:
            try:
                client_socket.send(data_string)
            except Exception:
                self.logToConsole("Lost connection to one bluetooth device", 2)
                client_socket.close()
                self.client_sock_list.remove(client_socket)
