import time

import pyttsx3

from src.constants import Constants
from src.data_helpers import get_value_from_dictionary
from src.Modules.data_interface_core import ThreadedModuleCore

ASCENT_LOGGING_STATES = [
    Constants.fcb_state_names[Constants.POWERED_ASCENT_STATE_INDEX],
    Constants.fcb_state_names[Constants.COAST_TO_APOGEE_INDEX],
]
DESCENT_LOGGING_STATES = [
    Constants.fcb_state_names[Constants.DROGUE_DESCENT_INDEX],
    Constants.fcb_state_names[Constants.MAIN_DESCENT_INDEX],
]


class TextToSpeech(ThreadedModuleCore):
    """
    Yells at you
    """

    def __init__(self):
        super().__init__()
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 180)  # setting up new voice rate
        self.engine.setProperty("voice", "english_wmids")  # Bad Australian
        # voices = self.engine.getProperty('voices') #Un comment this to see a list of voices
        # print([a.id for a in voices])

        self.last_state = ""
        self.last_pyro_status = []

        self.last_speech_time = 0
        self.ascent_speech_interval_seconds = 5
        self.descent_interval_seconds = 10

    def spin(self):
        state = get_value_from_dictionary(self.gui_full_data_dictionary, Constants.fcb_state_key, "")
        altitude = get_value_from_dictionary(self.gui_full_data_dictionary, Constants.altitude_key, "Invalid Altitude")
        v_speed = get_value_from_dictionary(self.gui_full_data_dictionary, Constants.vertical_speed_key, "Invalid Vertical Speed")
        pyro_status = get_value_from_dictionary(self.gui_full_data_dictionary, Constants.pyro_fire_status, [])

        # Make sure these two are the same length
        # Should only run once when we get the first data point
        if len(pyro_status) != len(self.last_pyro_status):
            self.last_pyro_status = pyro_status.copy()

        if state == "":
            return

        # Read out state changes
        if state != self.last_state:
            if self.last_state == Constants.fcb_state_names[Constants.PREFLIGHT_STATE_INDEX]:  # If we're going out of preflight (happens when launch is detected)
                self.last_speech_time = time.time()

            self.speak_message(state)
            self.last_state = state

        # Read out pyro changes
        for i in range(len(pyro_status)):
            pyro = pyro_status[i]
            last_loop_pyro = self.last_pyro_status[i]

            if pyro and not last_loop_pyro:
                self.speak_message("Pyro {} fired".format(i + 1))  # Pyros are numbered from 1

        self.last_pyro_status = pyro_status.copy()

        # Read out altitude and velocity
        if state in ASCENT_LOGGING_STATES and time.time() - self.ascent_speech_interval_seconds > self.last_speech_time:
            log_message = "Altitude: {} meters".format(int(altitude))
            self.speak_message(log_message)
        elif state in DESCENT_LOGGING_STATES and time.time() - self.descent_interval_seconds > self.last_speech_time:
            log_message = "Altitude: {0} meters, Descent rate: {1} meters per second".format(int(altitude), abs(int(v_speed)))
            self.speak_message(log_message)
        else:
            return

    def speak_message(self, message):
        self.engine.say(message)
        self.engine.runAndWait()
        self.last_speech_time = time.time()
