#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand

from __future__ import absolute_import, division, print_function

import threading

from mcculw import ul
from mcculw.enums import (
    ScanOptions,
    ChannelType,
    FunctionType,
    AnalogInputMode,
    DigitalIODirection,
    InterfaceType,
    TrigType
)
from mcculw.ul import ULError

from lambda_scope.devices.ul_helpers import util
from lambda_scope.devices.ul_helpers.ao import AnalogOutputProps
from lambda_scope.devices.ul_helpers.ai import AnalogInputProps
from lambda_scope.devices.ul_helpers.digital import DigitalProps

class DAQDevice():
    """This is a DAQ device."""

    def __init__(
            self,
            serial_num,
            board_num):

        self.serial_num = serial_num
        self.board_num = board_num

        if not self.board_num:
            ul.ignore_instacal()

        self.configure_daq_device()

        self.ao_props = AnalogOutputProps(self.board_num)
        self.ao_range = self.ao_props.available_ranges[0]

        self.ai_props = AnalogInputProps(self.board_num)
        self.ai_range = self.ai_props.available_ranges[0]

        self.d_props = DigitalProps(self.board_num)
        self.d_port = self.d_props.port_info[0]

        ul.d_config_port(self.board_num, self.d_port.type, DigitalIODirection.OUT)

        ul.set_trigger(self.board_num, TrigType.TRIG_HIGH, 0, 1)

    def configure_daq_device(self):
        """Create a device object within the Universal Library
        for the DAQ device specified by the serial number."""

        devices = ul.get_daq_device_inventory(InterfaceType.USB)
        if devices:
            for device in devices:
                if device.unique_id == self.serial_num:
                    ul.create_daq_device(self.board_num, device)
                    print("DAQ {}: Initialized.".format(self.serial_num))
                    ul.a_input_mode(self.board_num, AnalogInputMode.SINGLE_ENDED)
            print("DAQ {}: Not Found.".format(self.serial_num))
        print("No DAQ Device Found.")

    def v_out(self, chan_num, voltage_value):
        """Output voltage_value from channel chan_num."""
        try:
            ul.v_out(self.board_num, chan_num, self.ao_range, voltage_value)
        except ULError as _e:
            util.print_ul_error(_e)

    def v_in(self, chan_num):
        """Return the inputs voltage to the channel chan_num."""
        try:
            input_voltage = ul.v_in(self.board_num, chan_num, self.ai_range)
        except ULError as _e:
            util.print_ul_error(_e)
        return input_voltage

    def d_out(self, port_value):
        """Outputs port_value from the digital port"""
        try:
            ul.d_out(self.board_num, self.d_port.type, port_value)
        except ULError as _e:
            util.print_ul_error(_e)

    def d_bit_out(self, bit_num, bit_value):
        """Outputs the bit_value (0 or 1) from bit bit_num"""
        try:
            ul.d_bit_out(self.board_num, self.d_port.type, bit_num, bit_value)
        except ULError as _e:
            util.print_ul_error(_e)

    def a_out_scan(self, low_chan, high_chan, npoints, rate, background=False,
                   continuous=False, extclock=False, exttrigger=False):
        """Outputs values to a range of D/A channels. This function can be used for
        paced analog output on hardware that supports paced output. It can also be
        used to update all analog outputs at the same time when the SIMULTANEOUS
        option is used."""

        options = background * ScanOptions.BACKGROUND \
                  |continuous * ScanOptions.CONTINUOUS \
                  |extclock * ScanOptions.EXTCLOCK \
                  |exttrigger * ScanOptions.EXTTRIGGER
        try:
            output_rate = ul.a_out_scan(board_num=self.board_num,
                                        low_chan=low_chan,
                                        high_chan=high_chan,
                                        num_points=npoints,
                                        rate=rate,
                                        ul_range=self.ao_range,
                                        memhandle=self.memhandle,
                                        options=options)
        except ULError as _e:
            util.print_ul_error(_e)
        return output_rate

    def stop_background(self):
        """Stops one or more subsystem background operations that are in progress for
        the specified board. Use this function to stop any function that is running in
        the background. This includes any function that was started with the
        :const:~pyulmcculwms.ScanOptions.BACKGROUND option."""
        try:
            ul.stop_background(self.board_num, FunctionType.AOFUNCTION)
        except ULError as _e:
            util.print_ul_error(_e)

    def allocate_buffer(self, npoints):
        """Allocates a buffer and creates a ctypes array."""

        self.memhandle = ul.win_buf_alloc(npoints)
        if self.memhandle:
            self.ctypes_array = util.memhandle_as_ctypes_array(self.memhandle)
            return True

        print("DAQ {}: Failed to allocate memory.".format(self.serial_num))
        return False

    def fill_ctypes_array(self, index, voltage_value):
        """Converts the voltage_value and uses index to fill the array."""
        value = ul.from_eng_units(self.board_num, self.ao_range, voltage_value)
        self.ctypes_array[index] = value

    def free_buffer(self):
        """Frees a Windows global memory buffer which was previously allocated with
        :func:.win_buf_alloc, :func:.win_buf_alloc_32, :func:.win_buf_alloc_64 or
        :func:.scaled_win_buf_alloc."""
        try:
            ul.win_buf_free(self.memhandle)
        except ULError as _e:
            util.print_ul_error(_e)

    def release(self):
        """Removes the specified DAQ device from the Universal Library, and releases
        all resources associated with that device."""
        try:
            ul.release_daq_device(self.board_num)
        except ULError as _e:
            util.print_ul_error(_e)

    def shutdown(self):
        """Shuts down the device."""
        for i in range(self.ao_props.num_chans):
            self.v_out(i, 0)
        self.d_out(0)
        self.release()

