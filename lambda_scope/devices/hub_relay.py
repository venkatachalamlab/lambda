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
    --camera=NUMBER                     Camera number.
                                            [default: *]
    --format=UINT16_ZYX_22_512_1024     Image format.
                                            [default: UINT16_ZYX_25_512_1024]
    --mode_directory=PATH               Path to the json mode file.
                                        [default: C:/src/venkatachalamlab/software/python/vlab/vlab/devices/lambda_devices/]
"""

from typing import Tuple
import json
import time

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
            camera: str,
            mode_directory: str,
            fmt: str,
            name="hub"):

        Hub.__init__(self, inbound, outbound, server, name)

        (self.dtype, _, self.shape) = array_props_from_string(fmt)
        self.mode_directory = mode_directory
        self.mode_dict = {}

        if camera == "*":
            self.cameras = [1, 2]
        else:
            self.cameras = [int(camera)]


    # def set_mode(self, mode):
    #     """Reads the parameters from a json file and calls the methods to set them."""
    #     mode_file = self.mode_directory + "modes.json"
    #     with open(mode_file, 'r') as f:
    #         modes_dict = json.load(f)
    #         self.mode_dict = modes_dict[mode]

    #     self.stop()
    #     for i in range(4):
    #         self._laser_set_nd_filters(i + 1, self.mode_dict["nd_filters"][i])
    #         for j in range(4):
    #             self._daq_set_laser(i, self.mode_dict["laser_power"][i][j], j)
    #     self._daq_set_las_continuous(self.mode_dict["laser_output_continuous"])
    #     self._hdf_writer_set_writer_mode(self.mode_dict["writer_mode"])
    #     self._binary_writer_set_writer_mode(self.mode_dict["writer_mode"])
    #     self._camera_set_trigger_mode(self.mode_dict["camera_trigger_mode"])
    #     self._dragonfly_set_imaging_mode(self.mode_dict["dragonfly_imaging_mode"])
    #     self._camera_set_stack_size(self.mode_dict["stack_size"])
    #     self._noise_filter_set_stack_size(self.mode_dict["stack_size"])
    #     self._hdf_writer_set_stack_size(self.mode_dict["stack_size"])
    #     self._binary_writer_set_stack_size(self.mode_dict["stack_size"])
    #     self._daq_set_stack_size(self.mode_dict["stack_size"])
    #     self._mip_maker_set_stack_size(self.mode_dict["stack_size"])
    #     self._image_displayer_set_format(self.z_scale*self.mode_dict["stack_size"]+self.shape[1],
    #                                      self.z_scale*self.mode_dict["stack_size"]+self.shape[2])
    #     self._daq_set_voltage_step(self.mode_dict["voltage_step"])
    #     self._daq_set_rate(self.mode_dict["rate"])
    #     self._dragonfly_set_filter(1, self.mode_dict["filter1"])
    #     self._dragonfly_set_filter(2, self.mode_dict["filter2"])
    #     self._timer_set_timer(self.mode_dict["timer_on"], self.mode_dict["timer_off"])
    #     self._dragonfly_set_fieldstop(self.mode_dict["dragonfly_fieldstop"])

    #     print("mode "+ str(mode) + " is set.")


    # def start(self):
    #     """It publishes the stop command to each device."""
    #     self._camera_start()
    #     self._hdf_writer_start()
    #     self._binary_writer_start()
    #     self._mip_maker_start()
    #     self._noise_filter_start()
    #     self._timer_start()
    #     #important
    #     time.sleep(2)
    #     self._daq_start()

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


    # def stop(self):
    #     """It publishes the stop command to each device."""

    #     self._camera_stop()
    #     # self._runner_stop()

    #     # this delay provides all of other devices with enough time
    #     # to process any images that are already publishsed by the camera
    #     time.sleep(2)
    #     self._timer_stop()
    #     self._noise_filter_stop()
    #     self._hdf_writer_stop()
    #     self._binary_writer_stop()
    #     self._mip_maker_stop()

    #     # DAQ should stop after the camera,
    #     self._daq_stop()

    def update_status(self):
        "Asks devices to publsih their status."

    #     self._noise_filter_publish_status()
    #     self._hdf_writer_publish_status()
    #     self._binary_writer_publish_status()
        self._dragonfly_publish_status()
    #     self._daq_publish_status()
    #     self._camera_publish_status()
    #     self._runner_publish_status()
    #     self._valve_publish_status()

    def shutdown(self):
        """Send shutdown command to all devices."""

        self._displayer_shutdown()
        self._dragonfly_shutdown()
    #     self._hdf_writer_shutdown()
    #     self._binary_writer_shutdown()
    #     self._mip_maker_shutdown()
    #     self._noise_filter_shutdown()
    #     self._timer_shutdown()
    #     self._daq_shutdown()
    #     self._camera_shutdown()
    #     # self._valve_shutdown()
    #     self._runner_shutdown()
        time.sleep(5)
        self.running = False

    def _displayer_set_lookup_table(self, lut_low, lut_high):
        for i in self.cameras:
            name = "displayer{}".format(i)
            self.send("{} set_lookup_table {} {}".format(name, lut_low, lut_high))

    def _displayer_set_shape(self, z, y, x):
        for i in self.cameras:
            name = "displayer{}".format(i)
            self.send("{} set_shape {} {} {}".format(name, z, y, x))

    def _displayer_shutdown(self):
        for i in self.cameras:
            name = "displayer{}".format(i)
            self.send("{} shutdown".format(name))

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

######  These send the commands to the noise_filter device(s).

    # def _noise_filter_set_stack_size(self, stack_size):
    #     for i in range(self.ncameras):
    #         device_name = "noise_filter{}".format(i+self.camera_number)
    #         self.send("{} set_stack_size {}".format(device_name, stack_size))

    # def _noise_filter_publish_status(self):
    #     for i in range(self.ncameras):
    #         device_name = "noise_filter{}".format(i+self.camera_number)
    #         self.send(device_name + " publish_status")

    # def _noise_filter_start(self):
    #     for i in range(self.ncameras):
    #         device_name = "noise_filter{}".format(i+self.camera_number)
    #         self.send(device_name + " start")

    # def _noise_filter_stop(self):
    #     for i in range(self.ncameras):
    #         device_name = "noise_filter{}".format(i+self.camera_number)
    #         self.send(device_name + " stop")

    # def _noise_filter_shutdown(self):
    #     for i in range(self.ncameras):
    #         device_name = "noise_filter{}".format(i+self.camera_number)
    #         self.send(device_name + " shutdown")

######  These send the commands to the camera(s).

    # def _camera_set_stack_size(self, stack_size):
    #     for i in range(self.ncameras):
    #         device_name = "ZylaCamera{}".format(i+self.camera_number)
    #         self.send("{} set_stack_size {}".format(device_name, stack_size))

    # def _camera_set_trigger_mode(self, trigger_mode):
    #     for i in range(self.ncameras):
    #         device_name = "ZylaCamera{}".format(i+self.camera_number)
    #         self.send("{} set_trigger_mode {}".format(device_name, trigger_mode))

    # def _camera_publish_status(self):
    #     for i in range(self.ncameras):
    #         device_name = "ZylaCamera{}".format(i+self.camera_number)
    #         self.send(device_name + " publish_status")

    # def _camera_start(self):
    #     for i in range(self.ncameras):
    #         device_name = "ZylaCamera{}".format(i+self.camera_number)
    #         self.send(device_name + " start")

    # def _camera_stop(self):
    #     for i in range(self.ncameras):
    #         device_name = "ZylaCamera{}".format(i+self.camera_number)
    #         self.send(device_name + " stop")

    # def _camera_shutdown(self):
    #     for i in range(self.ncameras):
    #         device_name = "ZylaCamera{}".format(i+self.camera_number)
    #         self.send(device_name + " shutdown")


######  These send the commands to the DAQ.

    # def _daq_set_rate(self, rate):
    #     self.send("DAQ set_rate {}".format(rate))

    # def _daq_set_led(self, percentage):
    #     self.send("DAQ set_led {}".format(percentage))

    # def _daq_set_stack_size(self, stack_size):
    #     self.send("DAQ set_stack_size {}".format(stack_size))

    # def _daq_set_las_continuous(self, las_continuous):
    #     self.send("DAQ set_las_continuous {}".format(las_continuous))

    # def _daq_set_voltage_step(self, voltage_step):
    #     self.send("DAQ set_voltage_step {}".format(voltage_step))

    # def _daq_set_laser(self, idx, power, position):
    #     self.send("DAQ set_laser {} {} {}".format(idx, power, position))

    # def _daq_stop(self):
    #     self.send("DAQ stop")

    # def _daq_stop_green(self):
    #     self.send("DAQ green_laser_stop")

    # def _daq_laser_stop(self):
    #     self.send("DAQ laser_stop")

    # def _daq_single_laser(self, laser_index, laser_power_percentage):
    #     self.send("DAQ single_laser {} {}".format(laser_index, laser_power_percentage))

    # def _daq_start(self):
    #     self.send("DAQ start")

    # def _daq_shutdown(self):
    #     self.send("DAQ shutdown")

    # def _daq_publish_status(self):
    #     self.send("DAQ publish_status")

###### These send the commands to the led_controller

    # def set_optogenetics_params(self, n_pulse, t_on, t_off):
    #     self.send("led set_params {} {} {}".format(n_pulse, t_on, t_off))

    # def start_optogenetics(self):
    #     self.send("led start_experiment")

    # def stop_optogenetics(self):
    #     self.send("led stop_experiment")

    # def _led_shutdown(self):
    #     self.send("led shutdown")

######  These send the commands to the hdf_writer(s).

    # def _hdf_writer_set_writer_mode(self, writer_mode):
    #     for i in range(self.ncameras):
    #         device_name = "hdf_writer{}".format(i+self.camera_number)
    #         self.send("{} update_mode {}".format(device_name, writer_mode))

    # def _hdf_writer_set_stack_size(self, stack_size):
    #     for i in range(self.ncameras):
    #         device_name = "hdf_writer{}".format(i+self.camera_number)
    #         self.send("{} update_shape {}".format(device_name, stack_size))

    # def _hdf_writer_publish_status(self):
    #     for i in range(self.ncameras):
    #         device_name = "hdf_writer{}".format(i+self.camera_number)
    #         self.send(device_name + " publish_status")

    # def _hdf_writer_start(self):
    #     for i in range(self.ncameras):
    #         device_name = "hdf_writer{}".format(i+self.camera_number)
    #         self.send(device_name + " start")

    # def _hdf_writer_stop(self):
    #     for i in range(self.ncameras):
    #         device_name = "hdf_writer{}".format(i+self.camera_number)
    #         self.send(device_name + " stop")

    # def _hdf_writer_shutdown(self):
    #     for i in range(self.ncameras):
    #         device_name = "hdf_writer{}".format(i+self.camera_number)
    #         self.send(device_name + " shutdown")


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

######  These send the commands to the mip_maker.

    # def _mip_maker_start(self):
    #     self.send("mip_maker start")

    # def _mip_maker_stop(self):
    #     self.send("mip_maker stop")

    # def _mip_maker_shutdown(self):
    #     self.send("mip_maker shutdown")

    # def _mip_maker_set_stack_size(self, stack_size):
    #     self.send("mip_maker set_stack_size {}".format(stack_size))

    # def _mip_maker_publish_status(self):
    #     self.send("mip_maker publish_status")

######  These send the commands to the dragonfly_device.



######  These send the commands to the laser.

    # def _laser_set_nd_filters(self, laser_index, number_of_nd_filters):
    #     self.send("laser set_nd_filter {} {}".format(laser_index, number_of_nd_filters))

    # def _laser_shutdown(self):
    #     self.send("laser shutdown")



######  These send the commands to the valve.

    # def _valve_shutdown(self):
    #     self.send("valve shutdown")

    # def _valve_stop(self):
    #     self.send("valve stop")

    # def _valve_publish_status(self):
    #     self.send("valve publish_status")

######  These send the commands to the timer.

    # def _timer_start(self):
    #     self.send("timer start")

    # def _timer_stop(self):
    #     self.send("timer stop")

    # def _timer_shutdown(self):
    #     self.send("timer shutdown")

    # def _timer_set_timer(self, on_time, off_time):
    #     self.send("timer set_timer {} {}".format(on_time, off_time))


def main():
    """This is the hub for lambda."""
    arguments = docopt(__doc__)

    scope = LambdaHub(
        inbound=parse_host_and_port(arguments["--inbound"]),
        outbound=parse_host_and_port(arguments["--outbound"]),
        server=int(arguments["--server"]),
        mode_directory=arguments["--mode_directory"],
        fmt=arguments["--format"],
        camera=arguments["--camera"])

    scope.run()

if __name__ == "__main__":
    main()
