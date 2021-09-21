#! python
#
# This runs lambda.
#
# Copyright 2019
# Author: Vivek Venkatachalam, Mahdi Torkashvand



"""
Run all Lambda components.

Usage:
    lambda.py                           [options]

Options:
    -h --help                           Show this help.
    --format=UINT8_ZYX_22_512_1024      Image format.
                                            [default: UINT16_ZYX_25_512_512]
    --camera=<number>                   1 for camera1, 2 for camera2 and * to run both.
                                            [default: *]
"""

from subprocess import Popen
from os import kill
import signal
import time

from docopt import docopt

from vlab.zmq.type_utils import mip_fmt_from_fmt, array_props_from_string



def execute(job, fmt: str, camera: str):
    """This runs all devices."""

    if camera == "*":
        cameras = [1, 2]
    else:
        cameras = [int(camera)]

    dragonfly_usb_port = "COM9"
    serial_num_las_daq = "1D3B333"
    serial_num_cam_daq = "1D17835"

    ibound = str(5000)
    obound = str(5001)
    server = str(5002)

    # data_cam = 5003
    data_stamped = 5005

    # (_, _, shape) = array_props_from_string(fmt)

    # if shape[1:] == (512, 512):
    #     camera = "AndorZylaCamera_512_512_4"
    # elif shape[1:] == (256, 512):
    #     camera = "AndorZylaCamera_256_512_4"
    # elif shape[1:] == (512, 1024):
    #     camera = "AndorZylaCamera_512_1024_2"
    # elif shape[1:] == (1024, 1024):
    #     camera = "AndorZylaCamera_1024_1024_2"
    # elif shape[1:] == (1024, 2048):
    #     camera = "AndorZylaCamera_1024_2048_1"
    # elif shape[1:] == (2048, 2048):
    #     camera = "AndorZylaCamera_2048_2048_1"

    # serial_number = ["VSC-09002", "VSC-08793"]

    job.append(Popen(["lambda_hub",
                      "--inbound=L"  + obound,
                      "--outbound=L" + ibound,
                      "--server=" + server,
                      "--camera=" + camera,
                      "--format=" + fmt]))

    job.append(Popen(["lambda_client",
                      "--port=" + server]))

    job.append(Popen(["lambda_forwarder",
                      "--inbound="  + ibound,
                      "--outbound=" + obound]))

    job.append(Popen(["lambda_logger",
                      "--inbound="+ obound,
                      "--directory=C:/src/data/data_writer"]))

    job.append(Popen(["lambda_dragonfly",
                      "--inbound=L" + obound,
                      "--outbound=L"+ ibound,
                      "--port=" + dragonfly_usb_port]))

    job.append(Popen(["lambda_acquisition_board",
                      "--commands_in=L" + obound,
                      "--status_out=L"  + ibound,
                      "--format=" + fmt,
                      "--serial_num_daq1=" + serial_num_las_daq,
                      "--serial_num_daq0=" + serial_num_cam_daq]))

    # job.append(Popen(["experiment_runner_v2",
    #                   "--inbound=L" + forwarder_out,
    #                   "--outbound=L"+ forwarder_in,
    #                   "--file_directory=C:/src/venkatachalamlab/software/python/vlab/vlab/devices/microfluidics_devices/"]))

    for i, camera_number in enumerate(cameras):

        job.append(Popen(["lambda_displayer",
                          "--inbound=L" + str(data_stamped + i),
                          "--format=" + fmt,
                          "--commands=L" + obound,
                          "--name=displayer"+ str(camera_number)]))


    #     job.append(Popen(["timer",
    #                       "--inbound_commands=L" + forwarder_out,
    #                       "--outbound_commands=L" + forwarder_in,
    #                       "--inbound=L" + str(data_stacker + index-1),
    #                       "--outbound=" + str(data_timer + index-1),
    #                       "--imaging=" + str(imaging),
    #                       "--resting=" + str(resting)]))


    #     job.append(Popen(["noise_filter",
    #                       "--data_in=L" + str(data_cam +  index-1),
    #                       "--commands_in=L" + forwarder_out,
    #                       "--data_out=" + str(data_stacker + index-1),
    #                       "--status_out=localhost:" + forwarder_in,
    #                       "--format=" + fmt,
    #                       "--name=noise_filter"+ str(index)]))


    #     job.append(Popen(["mip_maker",
    #                       "--data_in=L" + str(data_stacker + index-1),
    #                       "--commands=L" + forwarder_out,
    #                       "--data_out=" + str(data_mip + index-1),
    #                       "--status_out=L" + forwarder_in,
    #                       "--z_scale=" + z_scale,
    #                       "--format=" + fmt]))


    #     job.append(Popen(["hdf_writer",
    #                       "--data_in=localhost:" + str(data_timer + index-1),
    #                       "--commands_in=localhost:" + forwarder_out,
    #                       "--status_out=localhost:" + forwarder_in,
    #                       "--format=" + fmt,
    #                       "--directory=C:/src/data/data_writer",
    #                       "--video_name=camera" + str(index),
    #                       "--name=hdf_writer"+ str(index)]))

        # job.append(Popen(["binary_writer",
        #                   "--data_in=localhost:" + str(data_timer + index-1),
        #                   "--commands_in=localhost:" + forwarder_out,
        #                   "--format=" + fmt,
        #                   "--directory=C:/src/data/data_writer",
        #                   "--video_name=camera" + str(index),
        #                   "--name=binary_writer"+ str(index)]))


    # if int(camera_number) in (1, 2):
    #     job.append(Popen([camera,
    #                       "--data=*:" + str(data_cam + int(camera_number) -1),
    #                       "--serial_number=" + serial_number[int(camera_number)-1],
    #                       "--trigger_mode=2",
    #                       "--stack_size=" + str(shape[0]),
    #                       "--name=ZylaCamera"+str(camera_number)]))

    # elif int(camera_number) == 3:
    #     job.append(Popen([camera,
    #                       "--data=*:" + str(data_cam),
    #                       "--serial_number=" + serial_number[0],
    #                       "--trigger_mode=2",
    #                       "--stack_size=" + str(shape[0]),
    #                       "--name=ZylaCamera1"]))

    #     time.sleep(20)
    #     job.append(Popen([camera,
    #                       "--data=*:" + str(data_cam + 1),
    #                       "--serial_number=" + serial_number[1],
    #                       "--trigger_mode=2",
    #                       "--stack_size=" + str(shape[0]),
    #                       "--name=ZylaCamera2"]))


def run(fmt: str, camera: str):
    """Run all system devices."""

    jobs = []

    def finish(*_):
        for job in jobs:
            try:
                job.kill()
            except PermissionError as _e:
                print("Received error closing process: ", _e)

        raise SystemExit

    signal.signal(signal.SIGINT, finish)

    execute(jobs, fmt, camera)

    while True:
        time.sleep(1)


def main():
    """CLI entry point."""
    args = docopt(__doc__)

    run(fmt=args["--format"], camera=args["--camera"])

if __name__ == "__main__":
    main()
