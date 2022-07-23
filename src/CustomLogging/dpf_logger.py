import datetime
import logging
import os
import time
from sys import stdout
from typing import Callable, List


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

    def __init__(self) -> None:

        if not os.path.exists("logs"):
            os.mkdir("logs")

        if not os.path.exists(LOGS_SUBDIR):
            os.mkdir(LOGS_SUBDIR)

        filename = f"{LOGS_SUBDIR}/logs.txt"

        self.stream = logging.StreamHandler(stdout)
        self.file = logging.FileHandler(f"{filename}", mode="a")
        formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s::%(funcName)s -> %(message)s")
        self.stream.setFormatter(formatter)
        self.file.setFormatter(formatter)

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


MAIN_GUI_LOGGER = DpfLogger()


class SerialLogger:

    # Pass __name__ again
    def __init__(self, name) -> None:
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
