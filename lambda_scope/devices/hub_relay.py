#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand, Vivek Venkatachalam

"""
This handles commands involving multiple devices.

Usage:
    hub_relay.py                        [options]

Options:
    -h --help                           Show this help.
    --inbound=HOST:PORT                 Connection for inbound messages.
                                            [default: localhost:5001]
    --outbound=HOST:PORT                Connection for outbound messages.
                                            [default: localhost:5000]
    --server=PORT                       Binding to server.
                                            [default: 5003]
    --zyla_camera=NUMBER                Camera number.
                                            [default: *]
    --flir_camera=NUMBER                Camera number.
                                            [default: *]
    --format=UINT16_ZYX_22_512_1024     Image format.
                                            [default: UINT16_ZYX_25_512_1024]
    --mode_directory=PATH               Path to the json mode file.
                                        [default: C:/src/venkatachalamlab/software/python/vlab/vlab/devices/lambda_devices/]
"""

import os
import json
import time
from typing import Tuple

from docopt import docopt

from lambda_scope.zmq.hub import Hub
from lambda_scope.zmq.utils import parse_host_and_port
from lambda_scope.devices.utils import array_props_from_string

class LambdaHub(Hub):
    """This is a central hub that is responsible for subscribing and publishing
    messages to all components of Lambda. Clients controlling the microscope
    should communicate only with this."""
    def __init__(
            self,
            inbound: Tuple[str, int, bool],
            outbound: Tuple[str, int, bool],
            server: int,
            zyla_camera: str,
            flir_camera: str,
            mode_directory: str,
            fmt: str,
            name="hub"):

        Hub.__init__(self, inbound, outbound, server, name)

        (self.dtype, _, self.shape) = array_props_from_string(fmt)
        self.mode_directory = mode_directory
        self.mode_dict = {}

        if zyla_camera == "*":
            self.zyla_cameras = [1, 2]
        else:
            self.zyla_cameras = [int(zyla_camera)]

        if flir_camera == "*":
            self.flir_cameras = [1, 2]
        else:
            self.flir_cameras = [int(flir_camera)]

    def set_mode(self, mode):
        mode_file = os.path.join(self.mode_directory , "modes.json")
        with open(mode_file, 'r') as f:
            modes_dict = json.load(f)
            self.mode_dict = modes_dict[mode]

        self.stop()
        for i in range(4):
            for j in range(4):
                self._daq_set_laser(i, self.mode_dict["laser_power"][i][j], j)
        self._daq_set_las_continuous(self.mode_dict["laser_output_continuous"])
        self._writer_set_saving_mode(self.mode_dict["saving_mode"])
        self._zyla_camera_set_trigger_mode(self.mode_dict["zyla_camera_trigger_mode"])
        self._dragonfly_set_imaging_mode(self.mode_dict["dragonfly_imaging_mode"])
        self.shape = self.mode_dict["shape"]
        self._zyla_camera_set_shape(*self.shape)
        self._writer_set_shape(*self.shape)
        self._data_hub_set_shape(*self.shape)
        self._displayer_set_shape(*self.shape)
        self._daq_set_stack_size(self.shape[0])
        self._daq_set_voltage_step(self.mode_dict["z_resolution_in_um"])
        self._daq_set_exposure_time(self.mode_dict["exposure_time"])
        self._dragonfly_set_filter(1, self.mode_dict["filter1"])
        self._dragonfly_set_filter(2, self.mode_dict["filter2"])
        self._data_hub_set_timer(self.mode_dict["total_volumes"], self.mode_dict["rest_time"])
        self._flir_camera_stop()
        self.bottom_scope_shape = self.mode_dict["bottom_scope_shape"]
        self._flir_camera_set_height(self.bottom_scope_shape[1])
        self._flir_camera_set_width(self.bottom_scope_shape[2])
        self._stage_data_hub_set_shape(*self.bottom_scope_shape)
        self._tracker_set_shape(*self.bottom_scope_shape)
        self._stage_writer_set_shape(*self.bottom_scope_shape)
        self._stage_displayer_set_shape(*self.bottom_scope_shape)
        self._stage_writer_set_saving_mode(self.mode_dict["bottom_scope_saving_mode"])
        self._tracker_set_crop_size(self.mode_dict["tracker_crop_size"])
        self._tracker_set_feat_size(self.mode_dict["tracker_feature_size"])
        self._tracker_set_camera_number(self.mode_dict["tracker_camera_source"])
        self.exposure, self.rate = self.mode_dict["bottom_scope_exposure_rate"]
        self._flir_camera_set_exposure(self.exposure, self.rate)
        self._tracker_set_rate(self.rate)
        self._zaber_set_limit_xy(self.mode_dict["stage_xy_limit"])
        self.max_xy_velocities = self.mode_dict["stage_max_velocities"]
        self._flir_camera_start()
        print("mode "+ str(mode) + " is set.")


    def start(self):
        self._zyla_camera_start()
        self._writer_start()
        self._stage_writer_start()
        self._data_hub_start()
        time.sleep(2) # Necessary
        self._daq_start()

    # def start_runner(self, mode):
    #     """Starts the runner."""
    #     self._runner_start(mode)

    # def run_mf_exp(self, img_mode, mf_mode):
    #     """Runs microfluidic experiments"""
    #     self.set_mode(img_mode)
    #     time.sleep(5)
    #     self.start()
    #     time.sleep(8)
    #     self._runner_start(mf_mode)

    # def run_np_exp(self):
    #     """runs the entire sexual dimorphism experiment"""
    #     self.set_mode("npc")
    #     time.sleep(5)
    #     self.start()
    #     time.sleep(8)
    #     self.stop()
    #     time.sleep(2)
    #     self.run_mf_exp("npa", "np_mf")


    def stop(self):
        self._zyla_camera_stop()
    #     # self._runner_stop()
        time.sleep(2) # Necessary
        self._data_hub_stop()
        self._writer_stop()
        self._stage_writer_stop()
        self._daq_stop() # DAQ should stop after the camera,

    def update_status(self):
        self._data_hub_publish_status()
        self._writer_publish_status()
        self._dragonfly_publish_status()
        self._daq_publish_status()
        self._zyla_camera_publish_status()
    #     self._runner_publish_status()
    #     self._valve_publish_status()

    def shutdown(self):
        self._dragonfly_shutdown()
        self._displayer_shutdown()
        self._writer_shutdown()
        self._data_hub_shutdown()
        self._daq_shutdown()
        self._zyla_camera_shutdown()
        self._flir_camera_shutdown()
        self._zaber_shutdown()
        self._stage_data_hub_shutdown()
        self._tracker_shutdown()
        self._stage_writer_shutdown()
        self._stage_displayer_shutdown()
    #     self._valve_shutdown()
    #     self._runner_shutdown()
        time.sleep(5)
        self._logger_shutdown()
        self.running = False

    def _logger_shutdown(self):
        self.send("logger shutdown")

    def _dragonfly_shutdown(self):
        self.send("dragonfly shutdown")

    def _dragonfly_publish_status(self):
        self.send("dragonfly publish_status")

    def _dragonfly_set_disk_dichroic(self, pos):
        self.send("dragonfly set_disk_dichroic {}".format(pos))

    def _dragonfly_set_emission_dichroic(self, pos):
        self.send("dragonfly set_emission_dichroic {}".format(pos))

    def _dragonfly_set_filter_speed(self, port, speed):
        self.send("dragonfly set_filter_speed {} {}".format(port, speed))

    def _dragonfly_set_filter(self, port, pos):
        self.send("dragonfly set_filter {} {}".format(port, pos))

    def _dragonfly_set_fieldstop(self, pos):
        self.send("dragonfly set_fieldstop {}".format(pos))

    def _dragonfly_set_imaging_mode(self, mode):
        self.send("dragonfly set_imaging_mode {}".format(mode))

    def _dragonfly_set_disk_speed(self, speed):
        self.send("dragonfly set_disk_speed {}".format(speed))

    def _dragonfly_set_standby(self, mode):
        self.send("dragonfly set_standby {}".format(mode))

    def _daq_set_exposure_time(self, exposure_time):
        self.send("daq set_exposure_time {}".format(exposure_time))

    def _daq_set_stack_size(self, stack_size):
        self.send("daq set_stack_size {}".format(stack_size))

    def _daq_set_las_continuous(self, las_continuous):
        self.send("daq set_laser_continuous {}".format(las_continuous))

    def _daq_set_voltage_step(self, z_resolution_in_um):
        self.send("daq set_voltage_step {}".format(float(z_resolution_in_um) / 10))

    def _daq_set_laser(self, idx, power, position):
        self.send("daq set_laser {} {} {}".format(idx, power, position))

    def _daq_stop(self):
        self.send("daq stop")

    def _daq_set_green_laser(self, power_percentage):
        self.send("daq set_green_laser {}".format(power_percentage))

    def _daq_set_green_led(self, led_status):
        self.send("daq set_green_led {}".format(led_status))

    def _daq_laser_stop(self):
        self.send("daq laser_stop")

    def _daq_single_laser(self, laser_index, power_percentage):
        self.send("daq single_laser {} {}".format(laser_index, power_percentage))

    def _daq_start(self):
        self.send("daq start")

    def _daq_shutdown(self):
        self.send("daq shutdown")

    def _daq_publish_status(self):
        self.send("daq publish_status")

    def _displayer_set_lookup_table(self, lut_low, lut_high):
        for i in self.zyla_cameras:
            name = "displayer{}".format(i)
            self.send("{} set_lookup_table {} {}".format(name, lut_low, lut_high))

    def _displayer_set_shape(self, z, y, x):
        for i in self.zyla_cameras:
            name = "displayer{}".format(i)
            self.send("{} set_shape {} {} {}".format(name, z, y, x))

    def _displayer_shutdown(self):
        for i in self.zyla_cameras:
            name = "displayer{}".format(i)
            self.send("{} shutdown".format(name))

    def _data_hub_set_shape(self, z, y, x):
        for i in self.zyla_cameras:
            name = "data_hub{}".format(i)
            self.send("{} set_shape {} {} {}".format(name, z, y, x))

    def _data_hub_set_timer(self, nvolumes, off_time):
        for i in self.zyla_cameras:
            name = "data_hub{}".format(i)
            self.send("{} set_timer {} {}".format(name, nvolumes, off_time))

    def _data_hub_start(self):
        for i in self.zyla_cameras:
            name = "data_hub{}".format(i)
            self.send("{} start".format(name))

    def _data_hub_stop(self):
        for i in self.zyla_cameras:
            name = "data_hub{}".format(i)
            self.send("{} stop".format(name))

    def _data_hub_shutdown(self):
        for i in self.zyla_cameras:
            name = "data_hub{}".format(i)
            self.send("{} shutdown".format(name))

    def _data_hub_publish_status(self):
        for i in self.zyla_cameras:
            name = "data_hub{}".format(i)
            self.send("{} publish_status".format(name))

    def _writer_set_saving_mode(self, saving_mode):
        for i in self.zyla_cameras:
            name = "writer{}".format(i)
            self.send("{} set_saving_mode {}".format(name, saving_mode))

    def _writer_set_shape(self, z, y, x):
        for i in self.zyla_cameras:
            name = "writer{}".format(i)
            self.send("{} set_shape {} {} {}".format(name, z, y, x))

    def _writer_start(self):
        for i in self.zyla_cameras:
            name = "writer{}".format(i)
            self.send("{} start".format(name))

    def _writer_stop(self):
        for i in self.zyla_cameras:
            name = "writer{}".format(i)
            self.send("{} stop".format(name))

    def _writer_shutdown(self):
        for i in self.zyla_cameras:
            name = "writer{}".format(i)
            self.send("{} shutdown".format(name))

    def _writer_publish_status(self):
        for i in self.zyla_cameras:
            name = "writer{}".format(i)
            self.send("{} publish_status".format(name))

    def _zyla_camera_set_stack_size(self, stack_size):
        for i in self.zyla_cameras:
            name = "ZylaCamera{}".format(i)
            self.send("{} set_stack_size {}".format(name, stack_size))

    def _zyla_camera_set_shape(self, z, y, x):
        for i in self.zyla_cameras:
            name = "ZylaCamera{}".format(i)
            self.send("{} set_shape {} {} {}".format(name, z, y, x))

    def _zyla_camera_set_trigger_mode(self, trigger_mode):
        for i in self.zyla_cameras:
            name = "ZylaCamera{}".format(i)
            self.send("{} set_trigger_mode {}".format(name, trigger_mode))

    def _zyla_camera_publish_status(self):
        for i in self.zyla_cameras:
            name = "ZylaCamera{}".format(i)
            self.send(name + " publish_status")

    def _zyla_camera_start(self):
        for i in self.zyla_cameras:
            name = "ZylaCamera{}".format(i)
            self.send(name + " start")

    def _zyla_camera_stop(self):
        for i in self.zyla_cameras:
            name = "ZylaCamera{}".format(i)
            self.send(name + " stop")

    def _zyla_camera_shutdown(self):
        for i in self.zyla_cameras:
            name = "ZylaCamera{}".format(i)
            self.send(name + " shutdown")

    def _flir_camera_start(self):
        for i in self.flir_cameras:
            name = "FlirCamera{}".format(i)
            self.send(name + " start")

    def _flir_camera_stop(self):
        for i in self.flir_cameras:
            name = "FlirCamera{}".format(i)
            self.send(name + " stop")

    def _flir_camera_shutdown(self):
        for i in self.flir_cameras:
            name = "FlirCamera{}".format(i)
            self.send(name + " shutdown")

    def _flir_camera_set_exposure(self, exposure, rate):
        for i in self.flir_cameras:
            name = "FlirCamera{}".format(i)
            self.send(name + " set_exposure {} {}".format(exposure, rate))

    def _flir_camera_set_height(self, height):
        for i in self.flir_cameras:
            name = "FlirCamera{}".format(i)
            self.send(name + " set_height {}".format(height))

    def _flir_camera_set_width(self, width):
        for i in self.flir_cameras:
            name = "FlirCamera{}".format(i)
            self.send(name + " set_width {}".format(width))

    def _zaber_clear_warnings(self):
        self.send("zaber clear_warnings")

    def _zaber_set_limit_xy(self, limit):
        self.send("zaber set_limit_xy {}".format(limit))

    def _zaber_set_max_velocities(self, max_vel_xy, max_vel_z):
        self.send("zaber set_max_velocities {} {}".format(max_vel_xy, max_vel_z))

    def _zaber_print_pos(self):
        self.send("zaber print_pos")

    def _zaber_home_z(self):
        self.send("zaber home_z")

    def _zaber_update_position(self):
        self.send("zaber update_position")

    def _zaber_stop_z(self):
        self.send("zaber stop_z")

    def _zaber_stop_xy(self):
        self.send("zaber stop_xy")

    def _zaber_shutdown(self):
        self.send("zaber shutdown")

    def _stage_data_hub_set_shape(self, z, y, x):
        for i in self.flir_cameras:
            name = "stage_data_hub{}".format(i)
            self.send(name + " set_shape {} {} {}".format(z, y, x))

    def _stage_data_hub_shutdown(self):
        for i in self.flir_cameras:
            name = "stage_data_hub{}".format(i)
            self.send(name + " shutdown")

    def _tracker_set_rate(self, rate):
        self.send("tracker set_rate {}".format(rate))

    def _tracker_set_camera_number(self, camera_number):
        self.send("tracker set_camera_number {}".format(camera_number))

    def _tracker_set_shape(self, z, y, x):
        self.send("tracker set_shape {} {} {}".format(z, y, x))

    def _tracker_set_feat_size(self, feat_size):
        self.send("tracker set_feat_size {}".format(feat_size))

    def _tracker_set_crop_size(self, crop_size):
        self.send("tracker set_crop_size {}".format(crop_size))

    def _tracker_start(self):
        self.send("tracker start")

    def _tracker_stop(self):
        self.send("tracker stop")

    def _tracker_shutdown(self):
        self.send("tracker shutdown")

    def _stage_writer_set_saving_mode(self, saving_mode):
        for i in self.flir_cameras:
            name = "stage_writer{}".format(i)
            self.send("{} set_saving_mode {}".format(name, saving_mode))

    def _stage_writer_set_shape(self, z, y, x):
        for i in self.flir_cameras:
            name = "stage_writer{}".format(i)
            self.send("{} set_shape {} {} {}".format(name, z, y, x))

    def _stage_writer_start(self):
        for i in self.flir_cameras:
            name = "stage_writer{}".format(i)
            self.send("{} start".format(name))

    def _stage_writer_stop(self):
        for i in self.flir_cameras:
            name = "stage_writer{}".format(i)
            self.send("{} stop".format(name))

    def _stage_writer_shutdown(self):
        for i in self.flir_cameras:
            name = "stage_writer{}".format(i)
            self.send("{} shutdown".format(name))

    def _stage_writer_publish_status(self):
        for i in self.flir_cameras:
            name = "stage_writer{}".format(i)
            self.send("{} publish_status".format(name))

    def _stage_displayer_set_lookup_table(self, lut_low, lut_high):
        for i in self.flir_cameras:
            name = "stage_displayer{}".format(i)
            self.send("{} set_lookup_table {} {}".format(name, lut_low, lut_high))
        self.send("tracker_displayer set_lookup_table {} {}".format(lut_low, lut_high))

    def _stage_displayer_set_shape(self, z, y, x):
        for i in self.flir_cameras:
            name = "stage_displayer{}".format(i)
            self.send("{} set_shape {} {} {}".format(name, z, y, x))
        self.send("tracker_displayer set_shape {} {} {}".format(z, y, x))

    def _stage_displayer_shutdown(self):
        for i in self.flir_cameras:
            name = "stage_displayer{}".format(i)
            self.send("{} shutdown".format(name))
        self.send("tracker_displayer shutdown")




######  These send the commands to the runner.

    # def _runner_stop(self):
    #     self.send("runner stop")

    # def _runner_start(self, mode):
    #     self.send("runner run " + mode)

    # def _runner_shutdown(self):
    #     self.send("runner shutdown")

    # def _runner_publish_status(self):
    #     self.send("runner publish_status")

######  These send the commands to the laser.

    # def _set_laser(self, wavelength, power):
    #     self.send("laser set_laser {} {}".format(wavelength, power))

    # def _laser_start(self):
    #     self.send("laser start")

    # def _laser_stop(self):
    #     self.send("laser stop")

    # def _laser_shutdown(self):
    #     self.send("laser shutdown")

    # def _laser_publish_status(self):
    #     self.send("laser publish_status")



######  These send the commands to the valve.

    # def _valve_shutdown(self):
    #     self.send("valve shutdown")

    # def _valve_stop(self):
    #     self.send("valve stop")

    # def _valve_publish_status(self):
    #     self.send("valve publish_status")


def main():
    """This is the hub for lambda."""
    arguments = docopt(__doc__)

    scope = LambdaHub(
        inbound=parse_host_and_port(arguments["--inbound"]),
        outbound=parse_host_and_port(arguments["--outbound"]),
        server=int(arguments["--server"]),
        mode_directory=arguments["--mode_directory"],
        fmt=arguments["--format"],
        zyla_camera=arguments["--zyla_camera"],
        flir_camera=arguments["--flir_camera"])

    scope.run()

if __name__ == "__main__":
    main()
