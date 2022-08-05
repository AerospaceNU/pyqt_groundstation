import datetime
import logging
import os
import time
from collections import OrderedDict
from sys import stdout
from typing import Callable, List

from src.CustomLogging.prop_logger import PropLogger


# Used to log to the console widget
class CustomHandler(logging.Handler):
    def __init__(self, callback, level=...) -> None:
        super().__init__(level)
        self.callback = callback

    def emit(self, record):
        try:
            msg = self.format(record)
            # issue 35046: merged two stream.writes into one.
            self.callback(record, msg)
        except RecursionError:  # See issue 36272
            raise
        except Exception:
            self.handleError(record)


START_TIME = datetime.datetime.now()
LOGS_SUBDIR = f"logs/{START_TIME.strftime('%m-%d-%Y_%H-%M-%S')}"


class DpfLogger:

    LOGGERS: List[logging.Logger] = []
    CUSTOM_HANDLERS: List[Callable[[logging.LogRecord], None]] = []
    formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s::%(funcName)s -> %(message)s")

    def __init__(self) -> None:

        if not os.path.exists("logs"):
            os.mkdir("logs")

        if not os.path.exists(LOGS_SUBDIR):
            os.mkdir(LOGS_SUBDIR)

        filename = f"{LOGS_SUBDIR}/logs.txt"

        self.stream = logging.StreamHandler(stdout)
        self.file = logging.FileHandler(f"{filename}", mode="a")
        self.stream.setFormatter(DpfLogger.formatter)
        self.file.setFormatter(DpfLogger.formatter)

    def change_dir(self):
        """
        Update the file logger to the newLOGS_SUBDIR
        """
        if not os.path.exists(LOGS_SUBDIR):
            os.mkdir(LOGS_SUBDIR)

        filename = f"{LOGS_SUBDIR}/logs.txt"
        file2 = logging.FileHandler(f"{filename}", mode="a")
        file2.setFormatter(DpfLogger.formatter)

        for logger in DpfLogger.LOGGERS:
            logger.removeHandler(self.file)
            logger.addHandler(file2)

        self.file = file2

    # Pass in __name__
    def get_logger(self, name) -> logging.Logger:
        log = logging.getLogger(name)
        DpfLogger.LOGGERS.append(log)

        log.setLevel("DEBUG")
        log.addHandler(self.stream)
        log.addHandler(self.file)

        for handler in DpfLogger.CUSTOM_HANDLERS:
            log.addHandler(handler)

        return log

    def add_custom_handler(self, function: Callable[[logging.LogRecord, str], None]):
        custom_handler = CustomHandler(function, "DEBUG")

        DpfLogger.CUSTOM_HANDLERS.append(custom_handler)

        for log in DpfLogger.LOGGERS:
            log.addHandler(custom_handler)

    def get_all_runs(self):
        """
        Get a list of dicts with this structure for each log file we have:
            name: (date, duration, has_groundstation, has_prop)
        """
        subpaths = os.listdir("logs")
        ret = {}
        for path in subpaths:
            try:
                main_log = open(f"logs/{path}/logs.txt").readlines()
                if len(main_log) < 1:
                    continue
                first_time = main_log[0].split(" : ")[0]
                first_time = time.strptime(first_time, "%Y-%m-%d %H:%M:%S,%f")
                last_time = main_log[-1].split(" : ")[0]
                last_time = time.strptime(last_time, "%Y-%m-%d %H:%M:%S,%f")
                duration = time.mktime(last_time) - time.mktime(first_time)

                groundstation_path = f"logs/{path}/GroundStationDataInterface_parsed.txt"
                if os.path.exists(groundstation_path):
                    has_groundstation_data = len(open(groundstation_path).readlines()) > 6  # RUN START takes up 5 lines
                else:
                    has_groundstation_data = False
                prop_path = f"logs/{path}/PROP_DATA_0.txt"
                if os.path.exists(prop_path):
                    has_prop_data = len(open(prop_path).readlines()) > 6  # RUN START takes up 5 lines
                else:
                    has_prop_data = False
                # has_prop_data = len(open(f"logs/{path}/").readlines()) > 6 # RUN START takes up 5 lines

                ret[path] = (time.mktime(first_time), duration, has_groundstation_data, has_prop_data)
            except Exception as e:
                print(e)

        # Sort by key (path), alphabetically. TODO This will only sorta work if dates are in the same year lol

        return OrderedDict(sorted(ret.items()))


MAIN_GUI_LOGGER = DpfLogger()
PROP_LOGGER = PropLogger(LOGS_SUBDIR)


class SerialLogger:
    LOGGERS = {}

    # Pass __name__ again
    def __init__(self, name) -> None:
        SerialLogger.LOGGERS[name] = self
        self.name = name
        self.raw_data_file = open(f"{LOGS_SUBDIR}/{name}_raw.txt", "a+")
        self.parsed_messages_file = open(f"{LOGS_SUBDIR}/{name}_parsed.txt", "a+")

        self.raw_data_file.write("\n\nRUN START {}\n\n".format(START_TIME.strftime("%Y-%m-%d %H:%M:%S")))
        self.parsed_messages_file.write("\n\nRUN START {}\n\n".format(START_TIME.strftime("%Y-%m-%d %H:%M:%S")))

    def write_raw(self, bytes):
        self.raw_data_file.write("{0}: {1}\n".format(time.strftime("%H:%M:%S"), str(bytes)))

    def write_parsed(self, message_type, parsed_message):
        self.parsed_messages_file.write("{0}: {1} {2}\n".format(time.strftime("%H:%M:%S"), message_type, str(parsed_message)))

    def close(self):
        self.raw_data_file.close()
        self.parsed_messages_file.close()


def set_test_name(test):
    # Need to CD into a new directory with a new name
    global LOGS_SUBDIR
    if test != "":
        LOGS_SUBDIR = f"logs/{START_TIME.strftime('%m-%d-%Y_%H-%M-%S')}_{test}"
    else:
        LOGS_SUBDIR = f"logs/{START_TIME.strftime('%m-%d-%Y_%H-%M-%S')}"

    # Need to change ever logger
    MAIN_GUI_LOGGER.change_dir()
    for logger in SerialLogger.LOGGERS:
        # We just need to call the ctor, really
        logger = SerialLogger.LOGGERS[logger]
        logger.close()
        logger.__init__(logger.name)

    # I kinda hate this
    PROP_LOGGER.__init__(LOGS_SUBDIR)
