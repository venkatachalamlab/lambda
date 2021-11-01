# !python
#
# Copyright 2021
# Authors: Mahdi Torkashvand

"""
This controls the piezo, cameras and the laser.

Usage:
    acquisition_board.py                          [options]

Options:
    -h --help                       Show this help.
    --commands_in=HOST:PORT         Socket address to receive messages.
                                        [default: localhost:5001]
    --status_out=HOST:PORT          Socket address to publish status
                                        [default: localhost:5000]
    --format=UINT16_ZYX_20_512_512  Size and type of image being sent.
                                        [default: UINT16_ZYX_25_512_1024]
    --serial_num_daq1=SERIAL        Serial number of the daq device connected to lasers.
                                        [default: 1D3B333]
    --serial_num_daq0=SERIAL        Serial number of the daq device connected to cameras.
                                        [default: 1D17835]
"""

from __future__ import absolute_import, division, print_function

import time
import json
from typing import Tuple

import zmq
import numpy as np
from docopt import docopt

from lambda_scope.zmq.publisher import Publisher
from lambda_scope.zmq.utils import parse_host_and_port
from lambda_scope.zmq.subscriber import ObjectSubscriber
from lambda_scope.devices.ul_helpers.daq import DAQDevice
from lambda_scope.devices.utils import array_props_from_string

class PiezoCameraLaserDAQ():
    """This is a DAQ device that subscribes from message forwarder"""

    def __init__(
            self,
            commands: Tuple[str, int, bool],
            outbound: Tuple[str, int, bool],
            fmt: str,
            serial_num_daq1: str,
            serial_num_daq0: str,
            name="daq"):

        self.status = {}
        self.name = name
        (self.dtype, _, self.shape) = array_props_from_string(fmt)
        self.low_chan_daq0 = 0
        self.high_chan_daq0 = 1
        self.low_chan_daq1 = 0
        self.high_chan_daq1 = 3
        self.laser_power = np.zeros((4, 4))
        self.voltage_step = 0.1
        self.stack_size = self.shape[0]

        self.n_increments = 4

        self.z_offset = 3.0
        self.if_buffer = 0
        self.initiated_flag_camera = 0
        self.initiated_flag_laser = 0
        self.device_status = 1
        self.laser_continuous = 0

        self.daq0 = DAQDevice(serial_num_daq0, 0)
        self.daq1 = DAQDevice(serial_num_daq1, 1)
        for i in range(4):
            self.daq1.v_out(i, 0)

        self._initialize()
        self._prepare_daq(self.z_offset)

        self.command_subscriber = ObjectSubscriber(
            obj=self,
            name=name,
            host=commands[0],
            port=commands[1],
            bound=commands[2])

        self.status_publisher = Publisher(
            host=outbound[0],
            port=outbound[1],
            bound=outbound[2])
        time.sleep(1)
        self.publish_status()

    def single_laser(self, idx, percentage_value):
        """Turns on the laser specified with idx."""
        if not self.initiated_flag_camera:
            if percentage_value == 0:
                value = 0
                self.daq1.v_out(idx, value)
            elif 0 < percentage_value <= 100:

                value = 0.4 + 3.6 * (percentage_value - 1) / 99
                self.daq1.v_out(idx, value)
            else:
                print("power percentage should be between 0 and 100.")
        else:
            print("To adjust a single laser, first send the stop command.")
        self.publish_status()


    def set_stack_size(self, stack_size):
        """Changes the shape of input and output array."""
        self.shape = (stack_size, self.shape[1], self.shape[2])
        self.stack_size = self.shape[0]
        self._initialize()
        self._prepare_daq(self.z_offset)
        self.publish_status()

    def set_voltage_step(self, voltagestep):
        """Sets the thickness of z steps."""
        self.voltage_step = voltagestep
        self._initialize()
        self._prepare_daq(self.z_offset)
        self.publish_status()

    def set_laser_continuous(self, is_continuous):
        """Sets the status of continuous scan option for the laser."""
        if is_continuous in ("True", True, "1", 1):
            self.laser_continuous = 1
        else:
            self.laser_continuous = 0
        self.publish_status()

    def set_exposure_time(self, exposure_time):
        """Set the closest valid exposure time."""
        self.n_increments = (exposure_time // 5) * 2
        self._initialize()
        self._prepare_daq(self.z_offset)
        self.publish_status()

    def set_laser(self, laser_idx, laser_power, laser_turn):
        """Sets the order that lasers are turned on, and the lasers power."""
        self.laser_power[laser_idx, laser_turn] = laser_power
        self._initialize()
        self._prepare_daq(self.z_offset)
        self.publish_status()

    def _initialize(self):
        """Sets the rate to a new value."""

        self.npoints_daq0 = 2 * self.n_increments * self.stack_size
        self.npoints_daq1 = 4 * 4 * self.n_increments * self.stack_size

        if self.if_buffer:
            self.daq0.free_buffer()
            self.daq1.free_buffer()

        self.if_buffer = self.daq0.allocate_buffer(self.npoints_daq0) & \
                         self.daq1.allocate_buffer(self.npoints_daq1)

        self._prepare_data()

    def _prepare_data(self):
        """Create the output data array based on values of steps and period """

        for i in range(self.stack_size):
            for j in range(self.n_increments):
                self.daq0.fill_ctypes_array(2 * (self.n_increments * i + j) + 0, self.z_offset + i * self.voltage_step)
                self.daq0.fill_ctypes_array(2 * (self.n_increments * i + j) + 1, (j % self.n_increments == 0) * 4.0)

        for i in range(4):
            for j in range(self.stack_size):
                for k in range(self.n_increments):
                    for l in range(4):
                        value = 0.0 if self.laser_power[l, i] == 0 else 0.4 + 3.6 * (self.laser_power[l, i] - 1) / 99.0
                        self.daq1.fill_ctypes_array(4 * (i * self.n_increments * self.stack_size + self.n_increments * j + k) + l, value)

    def _prepare_daq(self, destination):
        """Make the DAQ to initially output 0."""

        self.daq0.v_out(1, 0)
        cur_val_piezo = self.daq0.v_in(0)
        difference = destination - cur_val_piezo
        for i in range(100):
            self.daq0.v_out(0, cur_val_piezo + (difference/99)*i)
            time.sleep(0.005)

    def start(self):
        """Start outputing data from the DAQ.."""

        if not self.initiated_flag_camera:
            _ = self.daq0.a_out_scan(self.low_chan_daq0,
                                     self.high_chan_daq0,
                                     self.npoints_daq0,
                                     1,
                                     True, True, True, True)

            _ = self.daq1.a_out_scan(self.low_chan_daq1,
                                     self.high_chan_daq1,
                                     self.npoints_daq1,
                                     1,
                                     True, self.laser_continuous, True, True)

            self.daq0.d_out(1)

            self.initiated_flag_laser = 1
            self.initiated_flag_camera = 1
            self.publish_status()

    def stop(self):
        """Stop the DAQ."""

        self.laser_stop()
        if self.initiated_flag_camera:
            self.daq0.stop_background()
            self.initiated_flag_camera = 0

            self._prepare_daq(self.z_offset)
        self.publish_status()

    def laser_stop(self):
        """Stops the laser daq."""

        if self.initiated_flag_laser:
            self.daq1.stop_background()
            self.initiated_flag_laser = 0

        for i in range(4):
            self.daq1.v_out(i, 0)
        self.publish_status()

    def set_green_laser(self, power_percentage):
        self.daq1.stop_background()
        self.initiated_flag_laser = 0
        self.daq1.v_out(1, power_percentage)
        self.publish_status()

    def set_green_led(self, status):
        self.daq1.d_out(status)
        self.publish_status()

    def shutdown(self):
        """Shuts down the DAQ."""
        self.stop()
        self._prepare_daq(0)
        if self.if_buffer:
            self.daq0.free_buffer()
            self.daq1.free_buffer()
        self.daq0.release()
        self.daq1.release()
        self.device_status = 0
        self.publish_status()

    def update_status(self):
        """Updates the status dictionary."""
        self.status["voltage_step"] = self.voltage_step
        self.status["z_offset"] = self.z_offset
        self.status["stack_size"] = self.stack_size
        self.status["exposure_time"] = self.n_increments * 2.5
        self.status["405nm"] = np.array_str(self.laser_power[0, :])
        self.status["488nm"] = np.array_str(self.laser_power[1, :])
        self.status["561nm"] = np.array_str(self.laser_power[2, :])
        self.status["640nm"] = np.array_str(self.laser_power[3, :])
        self.status["laser_output_repeat"] = self.laser_continuous
        self.status["camera_runnig"] = self.initiated_flag_camera
        self.status["laser_running"] = self.initiated_flag_laser
        self.status["device"] = self.device_status

    def publish_status(self):
        """Publishes the status to the hub and logger."""
        self.update_status()
        self.status_publisher.send("hub " + json.dumps({self.name: self.status}, default=int))
        self.status_publisher.send("logger " + json.dumps({self.name: self.status}, default=int))

    def run(self):
        """Starts a while true loop and receives commands and handles them."""
        self.command_subscriber.flush()
        while self.device_status:
            self.command_subscriber.handle()

def main():
    """Create and start a DAQ
    Device object."""

    arguments = docopt(__doc__)

    device = PiezoCameraLaserDAQ(commands=parse_host_and_port(arguments["--commands_in"]),
                                 outbound=parse_host_and_port(arguments["--status_out"]),
                                 fmt=arguments["--format"],
                                 serial_num_daq1=arguments["--serial_num_daq1"],
                                 serial_num_daq0=arguments["--serial_num_daq0"])

    device.run()

if __name__ == "__main__":
    main()
