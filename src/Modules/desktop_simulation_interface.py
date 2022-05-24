import socket
import time

from src.Modules.ground_station_data_interface import GroundStationDataInterface

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8080  # The port used by the server


class LocalSimulationFlightInterface(GroundStationDataInterface):
    """
    Reads data from a local fcb simulation over tcp
    """

    def __init__(self):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.callbacks_to_add = []  # Don't add callbacks for radio and band switching (Kind of a hack)

        self.log_to_file = False

    def runOnEnableAndDisable(self):
        if self.enabled:
            try:
                self.logToConsole(
                    "Attempting to connect to local simulation at {0}:{1}".format(HOST, PORT),
                    1,
                )
                time.sleep(0.5)  # Sometimes we get enabled before the sim process is up
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Connects the socket when module is enabled
                self.socket.connect((HOST, PORT))
                self.logToConsole("Connected to local simulation at {0}:{1}".format(HOST, PORT), 1)
            except Exception as e:
                self.logToConsole(
                    "Could not connect to local simulation at {0}:{1}.  {2}".format(HOST, PORT, e),
                    2,
                )
                self.enabled = False
        else:
            self.socket.close()

    def recv_size(self):
        # 4 bytes appended to 128
        ret = self.socket.recv(132)

        return ret

    def spin(self):
        self.good_fcb_data = True
        self.connected = True
        # self.active_radio = 1
        self.has_data = True

        try:
            data = self.recv_size()
            self.parseData(data)
        except Exception as e:
            self.logToConsole(
                "Couldn't parse local simulation message: {0}, closing connection".format(e),
                2,
            )
            self.enabled = False

        self.updateEveryEnabledLoop()
