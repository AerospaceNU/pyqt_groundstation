"""Keep all custom exceptions in one place"""


class SerialPortDisconnectedError(RuntimeError):
    """Serial Port can't perform function because connection was closed."""

    def __init__(self, port_name: str):
        """
        Construct message with given port name.

        :param port_name: Name of port that was disconnected
        """
        super().__init__(f"{port_name} serial port closed")


class FcbNoAckError(RuntimeError):
    """FCB did not respond with an ACK"""

    def __init__(self, fcb_command: str):
        """
        Construct message with given FCB command

        :param fcb_command: FCB command that didn't respond
        """
        super().__init__(f"{fcb_command} command didn't respond")


class FcbIncompleteError(RuntimeError):
    """FCB did not respond with a completion identifier"""

    def __init__(self, fcb_command: str):
        """
        Construct message with given FCB command

        :param fcb_command: FCB command that didn't respond
        """
        super().__init__(f"{fcb_command} command didn't respond with completion")
