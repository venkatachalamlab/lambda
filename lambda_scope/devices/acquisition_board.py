#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand

"""
This controls the piezo, cameras and the laser.

Usage:
    acquisition_board.py           [options]

Options:
    -h --help                       Show this help.
    --commands_in=HOST:PORT         Socket address to receive messages.
                                        [default: localhost:5001]
    --status_out=HOST:PORT          Socket address to publish status
                                        [default: localhost:5000]
    --data_in=HOST:PORT             Connection for inbound array data.
                                        [default: L5008]
    --format=UINT16_ZYX_20_512_512  Size and type of image being sent. Allowed
                                    values: UINT8_YX_512_512, UINT8_YXC_512_512_3
                                        [default: UINT16_ZYX_25_512_1024]
    --voltage_step=<number>         Voltage difference between two steps.
                                        [default: 0.12]
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



from lambda_scope.devices.ul_helpers.daq import DAQDevice
from vlab.zmq.subscriber import ObjectSubscriber
from vlab.zmq.publisher import Publisher
from vlab.zmq.array import Subscriber
from vlab.zmq.type_utils import parse_host_and_port, array_props_from_string

_ZMQ_POLLER = zmq.Poller()
_ZMQ_POLLIN = zmq.POLLIN


class PiezoCameraLaserDAQ():
    """This is a DAQ device that subscribes from message forwarder"""

    def __init__(
            self,
            commands: Tuple[str, int, bool],
            outbound: Tuple[str, int, bool],
            data_in: Tuple[str, int, bool],
            fmt: str,
            voltage_step: float,
            serial_num_daq1: str,
            serial_num_daq0: str,
            name="DAQ"):

        self.status = {}
        self.name = name
        self.data_in = data_in
        (self.dtype, _, self.shape) = array_props_from_string(fmt)
        self.low_chan_daq0 = 0
        self.high_chan_daq0 = 1
        # self.led_chan_daq0 = 3
        self.low_chan_daq1 = 0
        self.high_chan_daq1 = 3
        self.laser_power = np.zeros((4, 4))
        self.voltage_step = voltage_step
        self.stack_size = self.shape[0]

        self.n = 2


        self.z_offset = 3.0
        self.if_buffer = 0
        self.initiated_flag_camera = 0
        self.initiated_flag_laser = 0
        self.device_status = 1
        self.poller = _ZMQ_POLLER
        self.las_continuous = False


        self.daq0 = DAQDevice(serial_num_daq0, 0)
        self.daq1 = DAQDevice(serial_num_daq1, 1)
        for i in range(4):
            self.daq1.v_out(i, 0)



        self._initialize()
        self._prepare_daq(self.z_offset)
        self.daq0.set_trigger(10, 0, 1)
        self.daq1.set_trigger(10, 0, 1)


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

        self.data_subscriber = Subscriber(
            host=self.data_in[0],
            port=self.data_in[1],
            datatype=self.dtype,
            shape=self.shape,
            bound=self.data_in[2])

        self.poller.register(self.command_subscriber.socket, _ZMQ_POLLIN)
        self.poller.register(self.data_subscriber.socket, _ZMQ_POLLIN)


    # def set_led(self, value_in_percent):
    #     """outputs voltage in range 5v from led channel."""
    #     if not self.initiated_flag_camera:
    #         voltage = 5 * value_in_percent / 100
    #         self.daq0.v_out(self.led_chan_daq0, voltage)
    #     else:
    #         print("To adjust the LED power, first send the stop command.")

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


    def set_stack_size(self, stack_size):
        """Changes the shape of input and output array."""
        self.shape = (stack_size, self.shape[1], self.shape[2])
        self.stack_size = self.shape[0]

        self.poller.unregister(self.data_subscriber.socket)
        self.data_subscriber.socket.close()
        self.data_subscriber = Subscriber(
            host=self.data_in[0],
            port=self.data_in[1],
            datatype=self.dtype,
            shape=self.shape,
            bound=self.data_in[2])
        self.poller.register(self.data_subscriber.socket, _ZMQ_POLLIN)

        self._initialize()
        self._prepare_daq(self.z_offset)

        self.update_status()
        self.publish_status()

    def set_voltage_step(self, voltagestep):
        """Sets the thickness of z steps."""
        self.voltage_step = voltagestep
        self._initialize()
        self._prepare_daq(self.z_offset)
        self.update_status()
        self.publish_status()

    def set_las_continuous(self, is_continuous):
        """Sets the status of continuous scan option for the laser."""
        if is_continuous in ("True", True, "1", 1):
            self.las_continuous = True
        else:
            self.las_continuous = False

    # def set_rate(self, rate):
    #     """Sets the rate at which the device outputs the ctype array."""
    #     self.rate = rate


    #     self._initialize()
    #     self._prepare_daq(self.z_offset)
    #     self.update_status()
    #     self.publish_status()

    def set_laser(self, laser_idx, laser_power, laser_turn):
        """Sets the order that lasers are turned on, and the lasers power."""
        self.laser_power[laser_idx, laser_turn] = laser_power
        self._initialize()
        self._prepare_daq(self.z_offset)
        self.update_status()
        self.publish_status()


    def _initialize(self):
        """Sets the rate to a new value."""

        self.npoints_daq0 = 2 * 2 * self.stack_size
        self.npoints_daq1 = 5 * 4 * 2 * self.stack_size



        if self.if_buffer:
            self.daq0.free_buffer()
            self.daq1.free_buffer()

        self.if_buffer = self.daq0.allocate_buffer(self.npoints_daq0) & \
                         self.daq1.allocate_buffer(self.npoints_daq1)

        self._prepare_data()



    def _prepare_data(self):
        """Create the output data array based on values of steps and period """

        for i in range(self.stack_size):
                for j in range(2):
                    self.daq0.fill_ctypes_array(2 * (2 * i + j) + 0, self.z_offset + i * self.voltage_step)
                    self.daq0.fill_ctypes_array(2 * (2 * i + j) + 1, (1 - j) * 4.0)

        self.daq1.fill_ctypes_array(4 * (2 * j + k) + 0, 0.0)
        self.daq1.fill_ctypes_array(4 * (2 * j + k) + 1, 0.0)
        self.daq1.fill_ctypes_array(4 * (2 * j + k) + 2, 0.0)
        self.daq1.fill_ctypes_array(4 * (2 * j + k) + 3, 0.0)


        for i in range(4):
            for j in range(self.stack_size):
                for k in range(2):

                    value0 = 0.0 if self.laser_power[0, i] == 0 else 0.4 + 3.6 * (self.laser_power[0, i] - 1) / 99.0
                    value1 = 0.0 if self.laser_power[1, i] == 0 else 0.4 + 3.6 * (self.laser_power[1, i] - 1) / 99.0
                    value2 = 0.0 if self.laser_power[2, i] == 0 else 0.4 + 3.6 * (self.laser_power[2, i] - 1) / 99.0
                    value3 = 0.0 if self.laser_power[3, i] == 0 else 0.4 + 3.6 * (self.laser_power[3, i] - 1) / 99.0

                    self.daq1.fill_ctypes_array(4 * ((i+1) * 2 * self.stack_size + 2 * j + k) + 0, value0)
                    self.daq1.fill_ctypes_array(4 * ((i+1) * 2 * self.stack_size + 2 * j + k) + 1, value1)
                    self.daq1.fill_ctypes_array(4 * ((i+1) * 2 * self.stack_size + 2 * j + k) + 2, value2)
                    self.daq1.fill_ctypes_array(4 * ((i+1) * 2 * self.stack_size + 2 * j + k) + 3, value3)


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
            self.daq_rate = self.daq0.a_out_scan(self.low_chan_daq0,
                                                 self.high_chan_daq0,
                                                 self.npoints_daq0,
                                                 self.daq_rate,
                                                 True, True, True, True)

            self.daq_rate = self.daq1.a_out_scan(self.low_chan_daq1,
                                                 self.high_chan_daq1,
                                                 self.npoints_daq1,
                                                 self.daq_rate,
                                                 True,
                                                 self.las_continuous, True, True)

            self.daq0.d_out(1)

            self.initiated_flag_laser = 1
            self.initiated_flag_camera = 1
            self.update_status()
            self.publish_status()


    def stop(self):
        """Stop the DAQ."""

        self.laser_stop()
        if self.initiated_flag_camera:
            self.daq0.stop_background()
            self.initiated_flag_camera = 0

            self._prepare_daq(self.z_offset)
            self.update_status()
            self.publish_status()

    def laser_stop(self):
        """Stops the laser daq."""

        if self.initiated_flag_laser:
            self.daq1.stop_background()
            self.initiated_flag_laser = 0

        for i in range(4):
            self.daq1.v_out(i, 0)
### added for optogenetic experiment

    def green_laser_stop(self):
        """Stops the laser daq."""
        if self.initiated_flag_laser:
            self.daq1.stop_background()
            self.initiated_flag_laser = 0
            self.daq1.v_out(1, 0)
            self.update_status()
            self.publish_status()

    # def set_laser(Laser_Idx, Laser_Power , Laser_Status)
    #     value = Laser_status * ( 0.4 + 3.6 * (Laser_Power - 1) / 99.0)
    #     for j in range
    #     self.daq1.fill_ctypes_array(4 * (Laser_Idx * 2 * self.stack_size + 2 * j + k) + 0, value0)

####


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
        self.update_status()
        self.publish_status()


    def update_status(self):
        """Updates the status dictionary."""
        self.status["voltage_step"] = self.voltage_step
        self.status["z_offset"] = self.z_offset
        self.status["stack_size"] = self.stack_size
        self.status["rate"] = self.daq_rate
        self.status["405nm"] = np.array_str(self.laser_power[0, :])
        self.status["488nm"] = np.array_str(self.laser_power[1, :])
        self.status["561nm"] = np.array_str(self.laser_power[2, :])
        self.status["640nm"] = np.array_str(self.laser_power[3, :])
        self.status["camera_signal_status"] = self.initiated_flag_camera
        self.status["laser_signal_status"] = self.initiated_flag_laser
        self.status["device_status"] = self.device_status

    def publish_status(self):
        """Publishes the status to the hub and logger."""
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
                                 data_in=parse_host_and_port(arguments["--data_in"]),
                                 fmt=arguments["--format"],
                                 voltage_step=float(arguments["--voltage_step"]),
                                 serial_num_daq1=arguments["--serial_num_daq1"],
                                 serial_num_daq0=arguments["--serial_num_daq0"])

    device.run()


if __name__ == "__main__":
    main()
