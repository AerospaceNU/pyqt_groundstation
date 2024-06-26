"""
Some test code to handle getting usb device names
"""

import re
import subprocess

import discotool
import serial.tools.list_ports
import serial.tools.list_ports_linux


def get_port_list_with_fancy_names():
    class FakePort:
        def __init__(self, device_name, description):
            self.device = device_name
            self.description = description

    deviceList, remainingPorts = discotool.usbinfos.get_devices_list()

    base_ports = []

    for device in deviceList:
        for port in device.ports:
            # base_ports.append(port)
            base_ports.append(FakePort(port["dev"], port["iface"]))

    return base_ports


def get_device_names():
    device_re = re.compile(
        r"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$",
        re.I,
    )
    df = subprocess.check_output("lsusb")
    devices = []
    for i in df.split(b"\n"):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo["device"] = "/dev/bus/usb/%s/%s" % (
                    dinfo.pop("bus"),
                    dinfo.pop("device"),
                )
                devices.append(dinfo)
    return devices


def listPorts():
    ports = list(serial.tools.list_ports.comports())

    for port in ports:
        print(get_port_data_dict_linux(port))


def get_port_data_dict_linux(port: serial.tools.list_ports):
    return {
        "name": port.name,
        "description": port.description,
        "port": port.device,
        "manufacturer": port.manufacturer,
        "pid": port.pid,
        "hwid": port.hwid,
        "interface": port.interface,
        "location": port.location,
        "product": port.product,
        "serial number": port.serial_number,
        "usb info": port.usb_info(),
        "usb description": port.usb_description(),
    }


if __name__ == "__main__":
    # device_data = get_device_names()
    # print(device_data)
    # listPorts()
    print(get_port_list_with_fancy_names())
