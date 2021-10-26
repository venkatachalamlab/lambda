#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand

"""
This controls zaber motors.

Usage:
    zaber.py                    [options]

Options:
    -h --help                   Show this help.
    --inbound=HOST:PORT         Socket address to receive commands.
                                    [default: localhost:5001]
    --outbound=HOST:PORT        Socket address to publish status.
                                    [default: localhost:5000]
    --usb_port_xy=<PORT>        USB port connected to the x-y controller.
                                    [default: COM6]
    --usb_port_z=<PORT>         USB port connected to the x-y controller.
                                    [default: COM5]
"""

import time
import json
from typing import Tuple

import numpy as np
from serial import Serial
from docopt import docopt

from lambda_scope.zmq.publisher import Publisher
from lambda_scope.zmq.subscriber import ObjectSubscriber
from lambda_scope.zmq.utils import parse_host_and_port

class ZaberController():
    """This controls x-y-z Zaber motors."""

    _COMMANDS = {"get_device_id": "/get deviceid\r",
                 "get_version": "/01 0 get version\r",
                 "get_system_access": "/01 0 get system.access\r",
                 "get_system_serial": "/01 0 get system.serial\r",
                 "get_system_axiscount": "/01 0 get system.axiscount\r",
                 "get_peripheral_id": "/01 0 get peripheralid\r",
                 "get_resolution": "/01 0 get resolution\r",
                 "vel": "/01 {axis} move vel {speed}\r",
                 "set_system_access": "/01 0 set system.access {n}\r",
                 "get_pos": "/01 0 get pos\r",
                 "set_limit_max": "/01 0 set limit.max {limit}\r",
                 "set_limit_min": "/01 0 set limit.min {limit}\r",
                 "set_pos": "/01 0 set pos {pos}\r",
                 "get_limit_max": "/01 0 get limit.max\r",
                 "get_limit_min": "/01 0 get limit.min\r",
                 "move_abs": "/01 {axis} move abs {pos}\r",
                 "set_maxspeed": "/01 0 set maxspeed {maxspeed}\r",
                 "get_maxspeed": "/01 0 get maxspeed\r",
                 "home": "/00 0 home\r",
                 "stop": "/00 0 stop\r",
                 "warning_clear": "/00 0 warnings clear\r"}

    def __init__(
            self,
            inbound: Tuple[str, int, bool],
            outbound: Tuple[str, int, bool],
            zaber_usb_port_xy="COM6",
            zaber_usb_port_z="COM5",
            name="zaber"):

        self.position = {}

        self.name = name
        self.device_status = 1
        self.is_port_open_z = 0
        self.is_port_open_xy = 0
        self.port_z = zaber_usb_port_z
        self.port_xy = zaber_usb_port_xy

        self.speed_z = 1.0
        self.mid_xy = 100000.0
        self.speed_max_z = 1000.0
        self.fine_speed_max_xy = 100.0
        self.coarse_speed_max_xy = 1000.0

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

        while not self.is_port_open_xy and not self.is_port_open_z:
            self.serial_obj_xy = Serial(port=self.port_xy, baudrate=115200, timeout=0)
            self.serial_obj_z = Serial(port=self.port_z, baudrate=115200, timeout=0)
            self.is_port_open_xy = self.serial_obj_xy.is_open
            self.is_port_open_z = self.serial_obj_z.is_open

        self.execute(self.serial_obj_xy, "set_system_access", n=2)
        self.execute(self.serial_obj_z, "set_system_access", n=2)

        self.clear_warnings()
        self.set_max_velocities(self.coarse_speed_max_xy, self.speed_max_z)

        self.stop_xy()
        self.set_limit_xy(10000)

        self.home_z()
        time.sleep(5)
        self.stop_z()

        self.clear_warnings()
        self.execute(self.serial_obj_z, "set_pos", pos=0)
        print("stage velocity in z direction: {} um/s".format(self.speed_z))
        print("Stage: Initialized.")

    def clear_warnings(self):
        self.execute(self.serial_obj_xy, "warning_clear")
        self.execute(self.serial_obj_z, "warning_clear")

    def set_limit_xy(self, limit):
        """Sets software limits for the motors."""
        upper_limit_pos = self.mid_xy + limit
        lower_limit_pos = self.mid_xy - limit

        half_way_data = data_from_pos_xy(self.mid_xy)
        upper_limit_data = data_from_pos_xy(upper_limit_pos)
        lower_limit_data = data_from_pos_xy(lower_limit_pos)

        self.execute(self.serial_obj_xy, "set_pos", pos=half_way_data)
        self.execute(self.serial_obj_xy, "set_limit_max", limit=upper_limit_data)
        self.execute(self.serial_obj_xy, "set_limit_min", limit=lower_limit_data)

    def set_max_velocities(self, max_velocity_xy, max_velocity_z):
        """Sets maximum allowed velocities."""
        max_velocity_data_xy = data_from_vel_xy(max_velocity_xy)
        max_velocity_data_z = data_from_vel_z(max_velocity_z)

        self.execute(self.serial_obj_xy, "set_maxspeed", maxspeed=max_velocity_data_xy)
        self.execute(self.serial_obj_z, "set_maxspeed", maxspeed=max_velocity_data_z)

    def get_pos_xy(self):
        """Returns the current position."""
        position = self.execute(self.serial_obj_xy, "get_pos")
        return pos_from_data_xy(int(position[-1])), pos_from_data_xy(int(position[-2]))

    def print_pos(self):
        """displays the current x, y and z location"""
        position_xy = self.get_pos_xy()
        position_z = self.execute(self.serial_obj_z, "get_pos")
        x = (position_xy[0] - self.mid_xy) / 1000
        y = (position_xy[1] - self.mid_xy) / 1000
        z = (pos_from_data_z(int(position_z[-2]))) / 1000
        print("(z, y, x) coordinate: ({}, {}, {})".format(round(z, 3), round(y, 3), round(x, 3)))

    def move_z(self, arg):
        """Starts moving in the direction specified by arg"""
        speed = arg * data_from_vel_z(self.speed_z)
        self.execute(self.serial_obj_z, "vel", axis=1, speed=speed)

    def home_z(self):
        """Sends z stage to its lowest point and sets the position to 0"""
        self.execute(self.serial_obj_z, "home")

    def change_vel_z(self, arg):
        """Changes velocity of z exponentially"""
        temp = self.speed_z * (2 ** arg)
        if 1.0 <= temp < self.speed_max_z:
            self.speed_z = np.rint(temp)

        print("stage velocity in z direction: {} um/s".format(self.speed_z))

    def fine_vel_xy(self, xspeed, yspeed):
        """Makes x and y motor to move at specified speeds."""
        xspeed_data = data_from_vel_xy(xspeed * self.fine_speed_max_xy)
        yspeed_data = data_from_vel_xy(yspeed * self.fine_speed_max_xy)
        self.execute(self.serial_obj_xy, "vel", axis=1, speed=yspeed_data)
        self.execute(self.serial_obj_xy, "vel", axis=2, speed=xspeed_data)

    def coarse_vel_xy(self, xspeed, yspeed):
        """Makes x and y motor to move at specified speeds."""
        xspeed_data = data_from_vel_xy(xspeed * self.coarse_speed_max_xy)
        yspeed_data = data_from_vel_xy(yspeed * self.coarse_speed_max_xy)
        self.execute(self.serial_obj_xy, "vel", axis=1, speed=yspeed_data)
        self.execute(self.serial_obj_xy, "vel", axis=2, speed=xspeed_data)

    def vel_xy(self, xspeed, yspeed):
        """Makes x and y motor to move at specified speeds."""
        xspeed_data = data_from_vel_xy(xspeed)
        yspeed_data = data_from_vel_xy(yspeed)
        self.execute(self.serial_obj_xy, "vel", axis=1, speed=yspeed_data)
        self.execute(self.serial_obj_xy, "vel", axis=2, speed=xspeed_data)

    def update_position(self):
        """Iquires the position and updates the logger."""
        self.position["X"], self.position["Y"] = self.get_pos_xy()
        self.status_publisher.send("logger "+ json.dumps({"position": self.position}, default=int))

    def stop_z(self):
        """Stops z axis"""
        self.execute(self.serial_obj_z, "stop")

    def stop_xy(self):
        """Stops x,y axes"""
        self.execute(self.serial_obj_xy, "stop")

    def shutdown(self):
        """Shuts down the device"""
        self.device_status = 0
        self.stop_z()
        self.stop_xy()
        self.execute(self.serial_obj_xy, "warning_clear")
        self.execute(self.serial_obj_z, "warning_clear")
        self.serial_obj_xy.close()
        self.serial_obj_z.close()
        self.serial_obj_xy.__del__()
        self.serial_obj_z.__del__()

    def run(self):
        """Starts a loop and receives and processes a message."""
        self.command_subscriber.flush()
        while self.device_status:
            req = self.command_subscriber.recv()
            self.command_subscriber.process(req)

    def execute(self, port, cmd, **kwargs):
        """Writes cmd on the port and returns the reply."""
        command = self._COMMANDS[cmd]
        command = command.format(**kwargs)

        port.write(bytes(command, "ascii"))

        r = b''
        while not r:
            r = port.readline()
        r = r.decode("utf-8")[1:-2]
        return r.split(" ")

def pos_from_data_z(data):
    return data * 2 / 21

def pos_from_data_xy(data):
    return data / 21

def vel_from_data_z(data):
    return data * 2 / 21 / 1.6384

def vel_from_data_xy(data):
    return data  / 21 / 1.6384

def data_from_pos_z(pos):
    return int(pos * 21 / 2)

def data_from_pos_xy(pos):
    return int(pos * 21)

def data_from_vel_z(vel):
    return int(vel * 21 * 1.6384 / 2)

def data_from_vel_xy(vel):
    return int(vel * 21 * 1.6384)

def main():
    """Create and start zaber devices."""

    arguments = docopt(__doc__)

    device = ZaberController(
        inbound=parse_host_and_port(arguments["--inbound"]),
        outbound=parse_host_and_port(arguments["--outbound"]),
        zaber_usb_port_xy=arguments["--usb_port_xy"],
        zaber_usb_port_z=arguments["--usb_port_z"])

    device.run()

if __name__ == "__main__":
    main()
