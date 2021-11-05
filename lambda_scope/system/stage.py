#! python
#
# This runs stage.
#
# Copyright 2021
# Author: Mahdi Torkashvand

"""
Run all stage components.

Usage:
    stage.py                            [options]

Options:
    -h --help                           Show this help.
    --format=UINT8_ZYX_22_512_1024      Image format.
                                            [default: UINT8_ZYX_1_512_512]
    --camera=<number>                   1 for camera1, 2 for camera2 and * to run both.
                                            [default: 1]
"""

import time
import signal
from subprocess import Popen

from docopt import docopt

from lambda_scope.devices.utils import array_props_from_string

def execute(job, fmt: str, camera: str):
    """This runs all devices."""

    forwarder_in = '192.168.170.111:5000'
    forwarder_out = '192.168.170.111:5001'

    saving_mode = "0"
    flir_exposure = "25000"
    XInputToZMQPub_out = str(6000)
    processor_out = str(6001)
    data_camera_out = 6002
    data_stamped = 6004
    tracker_out = str(6006)

    zaber_usb_port_xy = "COM6"
    zaber_usb_port_z = "COM5"

    serial_number = ["17549024", "17548830"]

    (_, _, shape) = array_props_from_string(fmt)

    if camera == "*":
        cameras = [1, 2]
    else:
        cameras = [int(camera)]

    data_directory = "D:/data/hdf_writer"

    job.append(Popen(["XInputToZMQPub",
                      "--outbound=*:" + XInputToZMQPub_out]))

    job.append(Popen(["lambda_processor",
                      "--inbound=L" + XInputToZMQPub_out,
                      "--outbound=" + processor_out,
                      "--deadzone=5000",
                      "--threshold=50"]))

    job.append(Popen(["lambda_commands",
                      "--inbound=L" + processor_out,
                      "--outbound=" + forwarder_in]))

    job.append(Popen(["lambda_zaber",
                      "--inbound=" + forwarder_out,
                      "--outbound=" + forwarder_in,
                      "--usb_port_xy=" + zaber_usb_port_xy,
                      "--usb_port_z=" + zaber_usb_port_z]))

    job.append(Popen(["lambda_stage_tracker",
                      "--commands_in=" + forwarder_out,
                      "--data_in=L" + str(data_stamped),
                      "--commands_out=" + forwarder_in,
                      "--data_out=" + tracker_out,
                      "--format=" + fmt]))

    job.append(Popen(["lambda_displayer",
                          "--inbound=L" + tracker_out,
                          "--format=" + fmt,
                          "--commands=" + forwarder_out,
                          "--name=tracking_displayer"]))

    job.append(Popen(["lambda_valve_control",
                      "--commands=" + forwarder_out,
                      "--status="+ forwarder_in]))

    for i, camera_number in enumerate(cameras):

        job.append(Popen(["lambda_displayer",
                          "--inbound=L" + str(data_stamped + i),
                          "--format=" + fmt,
                          "--commands=" + forwarder_out,
                          "--name=bottom_displayer"+ str(camera_number)]))

        job.append(Popen(["lambda_stage_data_hub",
                          "--data_in=L" + str(data_camera_out + i),
                          "--commands_in=" + forwarder_out,
                          "--status_out=" + forwarder_in,
                          "--data_out=" + str(data_stamped + i),
                          "--format=" + fmt,
                          "--name=stage_data_hub"+ str(camera_number)]))

        job.append(Popen(["lambda_writer",
                          "--data_in=L" + str(data_stamped + i),
                          "--commands_in=" + forwarder_out,
                          "--status_out=" + forwarder_in,
                          "--format=" + fmt,
                          "--saving_mode=" + saving_mode,
                          "--directory="+ data_directory,
                          "--video_name=camera" + str(camera_number),
                          "--name=stage_writer"+ str(camera_number)]))

        job.append(Popen(["FlirCamera",
                          "--serial_number=" + serial_number[int(camera_number)-1],
                          "--commands=" + forwarder_out,
                          "--name=FlirCamera"+str(camera_number),
                          "--status=" + forwarder_in,
                          "--data=*:" + str(data_camera_out + i),
                          "--width=" + str(shape[2]),
                          "--height=" + str(shape[1]),
                          "--exposure_time=" + flir_exposure]))

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
