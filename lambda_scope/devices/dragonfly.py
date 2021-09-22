#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand, Joshua Whitener

"""
This creates a dragonfly device.

Usage:
    dragonfly.py                [options]

Options:
    -h --help                   Show this help.
    --inbound=HOST:PORT         Socket address to receive commands.
                                    [default: localhost:5001]
    --outbound=HOST:PORT        Socket address to publish status.
                                    [default: localhost:5000]
    --port=<PORT>               USB port.
                                    [default: COM9]
"""

import json
import time
from typing import Tuple

from serial import Serial
from docopt import docopt

from lambda_scope.zmq.publisher import Publisher
from lambda_scope.zmq.subscriber import ObjectSubscriber
from lambda_scope.zmq.utils import parse_host_and_port

class DragonflyDevice():
    """This device subscribes to message forwarder, and sends command to dragonlfy spinning disk."""


    _COMMANDS = {
        "get_device_serial":"AT_SERIAL_CSU,?\r",

        "get_status":"AT_MS,?\r",
        "start_disk":"AT_MS_RUN\r",
        "stop_disk":"AT_MS_STOP\r",

        "get_standby":"AT_STANDBY,?\r",
        "set_standby":"AT_STANDBY,{standby_mode}\r",  # 0 or 1

        "get_disk_speed":"AT_MS,?\r",
        "set_disk_speed":"AT_MS,{speed}\r", # speed = 0 to 6000


        "get_modality":"AT_MODALITY,?\r",
        "set_modality_bf":"AT_MODALITY,BF\r",
        "set_modality_confocal":"AT_MODALITY,CONFOCAL\r",

        "get_confocal_mode":"AT_DC_SLCT,?\r",
        "set_confocal_25":"AT_DC_SLCT,2\r",
        "set_confocal_40":"AT_DC_SLCT,1\r",

        "get_fieldstop":"AT_AP_POS,1,?\r",
        "set_fieldstop":"AT_AP_POS,1,{fieldstop_mode}\r", # 1664-1404=1, 1404-1404=2,
                                                          # 133-133=3, 88-71=4, 82-82=5,
                                                          # 71-71=6, 67-67=7, 46-34=8,
                                                          #  41-41=9, 325-325=10

        "get_filter":"AT_FW_POS,{filter_port},?\r", # left=1, right=2
        "set_filter":"AT_FW_POS,{filter_port},{filter_number}\r", # LIST THE FILTERS HERE

        "get_filter_speed":"AT_FW_SPEED,{filter_port},?\r",
        "set_filter_speed":"AT_FW_SPEED,{filter_port},{filter_speed}\r", # port= 1 or 2,
                                                                         # filterspeed = 1, 2, or 3

        "get_emission_dichroic":"AT_PS_POS,1,?\r",
        "set_emission_dichroic":"AT_PS_POS,1,{emission}\r", # 100% pass=1, 100% reflect=2, 565P=3

        "get_disk_dichroic":"AT_DM_POS,1,?\r",
        "set_disk_dichroic":"AT_DM_POS,1,{dichroic}\r" # 488_561_640=1, empty=2
        }

    def __init__(
            self,
            inbound: Tuple[str, int, bool],
            outbound: Tuple[str, int, bool],
            port='COM9',
            name="dragonfly",):

        self.status = {}
        self.port = port
        self.is_port_open = 0
        self.name = name
        self.device_status = 1

        self.command_subscriber = ObjectSubscriber(
            obj=self,
            name=name,
            host=inbound[0],
            port=inbound[1],
            bound=inbound[2])

        self.status_publisher = Publisher(
            host=outbound[0],
            port=outbound[1],
            bound=outbound[2])

        while not self.is_port_open:
            self.serial_obj = Serial(port=self.port, baudrate=115200, timeout=0)
            self.is_port_open = self.serial_obj.is_open

        self._execute("set_standby", standby_mode=0)

        self._execute("set_disk_speed", speed=6000)
        self.speed_reply = self._execute("get_disk_speed")
        while find_digits(self.speed_reply) < 5950:
            self._execute("start_disk")
            self.speed_reply = self._execute("get_disk_speed")
            time.sleep(1)

        self._execute("set_modality_bf")

        self._execute("set_filter_speed", filter_port=1, filter_speed=2)
        self._execute("set_filter", filter_port=1, filter_number=2)

        self._execute("set_filter_speed", filter_port=2, filter_speed=2)
        self._execute("set_filter", filter_port=2, filter_number=2)

        self._execute("set_emission_dichroic", emission=3)

        self._execute("set_disk_dichroic", dichroic=1)
        self._execute("set_fieldstop", fieldstop_mode=2)

        self.publish_status()
        print("Dragonfly: Initialized")


    def set_standby(self, mode=0):
        """Sets the standby mode."""
        if mode in (0, 1):
            self._execute("set_standby", standby_mode=mode)
            self.publish_status()

    def set_disk_speed(self, speed=6000):
        """Sets the disk speed."""
        if 0 < speed < 6001:
            self._execute("set_disk_speed", speed=speed)
            reply = self._execute("get_disk_speed")

            while find_digits(reply) < (int(speed)-100):
                self._execute("start_disk")
                reply = self._execute("get_disk_speed")
            self.publish_status()

    def set_imaging_mode(self, mode):
        """Sets the confocal mode."""
        if mode in (1, 2, 3):
            if mode == 1:
                self._execute("set_modality_bf")

            elif mode in (2, 3):
                self._execute("set_modality_confocal")
                if mode == 2:
                    self._execute("set_confocal_40")
                else:
                    self._execute("set_confocal_25")
            self.publish_status()

    def set_fieldstop(self, mode):
        """Sets the imaging field of view."""
        if 0 < mode < 11:
            self._execute("set_fieldstop", fieldstop_mode=mode)
            self.publish_status()


    def set_filter(self, port, number):
        """Sets the Filter."""
        if 0 < number < 9:
            self._execute("set_filter", filter_port=port, filter_number=number)
            self.publish_status()

    def set_filter_speed(self, port, speed):
        """Sets the filter speed."""
        if 0 < speed < 4:
            self._execute("set_filter_speed", filter_port=port, filter_speed=speed)
            self.publish_status()

    def set_emission_dichroic(self, pos):
        """Sets the emission dichroic."""
        if 0 < pos < 4:
            self._execute("set_emission_dichroic", emission=pos)
            self.publish_status()

    def set_disk_dichroic(self, pos):
        """Sets disk dichroic."""
        if pos in (1, 2):
            self._execute("set_disk_dichroic", emission=pos)
            self.publish_status()

    def shutdown(self):
        """Shuts down the device"""
        self.device_status = 0
        self.publish_status()
        self._execute("stop_disk")
        self._execute("set_standby", standby_mode=1)
        self.serial_obj.close()
        self.serial_obj.__del__()

    def update_status(self):
        """Updates status dictionary."""

        self.status["disk_speed"] = find_digits(self._execute("get_disk_speed"))
        self.status["filter_1"] = self._execute("get_filter", filter_port=1)[:-3]
        self.status["filter_2"] = self._execute("get_filter", filter_port=2)[:-3]
        self.status["filter_1_speed"] = self._execute("get_filter_speed", filter_port=1)[:-3]
        self.status["filter_2_speed"] = self._execute("get_filter_speed", filter_port=2)[:-3]
        self.status["field_stop"] = self._execute("get_fieldstop")[:-3]
        self.status["Imaging Mode"] = self._execute("get_modality")[:-3]
        self.status["Disc Dichroic"] = self._execute("get_disk_dichroic")[:-3]
        self.status["Emission Dichroic"] = self._execute("get_emission_dichroic")[:-3]
        if self._execute("get_confocal_mode")[:-3] == "1":
            self.status["Pinhole Size"] = "40um"
        elif self._execute("get_confocal_mode")[:-3] == "2":
            self.status["Pinhole Size"] = "25um"
        elif self._execute("get_confocal_mode")[:-3] == "-1":
            self.status["Pinhole Size"] = "NA"
        self.status["device_status"] = self.device_status

    def publish_status(self):
        """Publishes the status to the hub and logger."""
        self.update_status()
        self.status_publisher.send("hub " + json.dumps({self.name: self.status}, default=int))
        self.status_publisher.send("logger "+ json.dumps({self.name: self.status}, default=int))

    def _execute(self, cmd: str, **kwargs):

        cmd_format_string = self._COMMANDS[cmd]
        formatted_string = cmd_format_string.format(**kwargs)
        reply = b''
        self.serial_obj.write(bytes(formatted_string, "ascii"))
        while not reply:
            reply = self.serial_obj.readline()
        return reply.decode("utf-8")

    def run(self):
        """Starts a loop and receives and processes a message."""
        self.command_subscriber.flush()
        while self.device_status:
            req = self.command_subscriber.recv()
            self.command_subscriber.process(req)



def find_digits(message):
    """Returns the digits in a string message."""

    number = ""
    for i in message:
        if i.isdigit():
            number = number + i
    if not number:
        number = "0"
    return int(number)




def main():
    """Create and start DragonflyDevice."""

    arguments = docopt(__doc__)

    device = DragonflyDevice(
        inbound=parse_host_and_port(arguments["--inbound"]),
        outbound=parse_host_and_port(arguments["--outbound"]),
        port=arguments["--port"])

    device.run()

if __name__ == "__main__":
    main()
