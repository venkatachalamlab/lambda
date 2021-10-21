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
                                            [default: UINT16_ZYX_25_512_512]
    --camera=<number>                   1 for camera1, 2 for camera2 and * to run both.
                                            [default: *]
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

    XInputToZMQPub_out = str(6000)
    processor_out = str(6001)

    zaber_usb_port_xy = "COM6"
    zaber_usb_port_z = "COM5"

    # (_, _, shape) = array_props_from_string(fmt)


    # if camera == "*":
    #     cameras = [1, 2]
    # else:
    #     cameras = [int(camera)]

    # serial_number = ["17549024", "????????"]

    # data_directory = "D:/data/hdf_writer"


    # displayer_fmt = "UINT8_YX_" + str(shape[0]) + "_" + str(shape[1])
    # filter_fmt = "UINT8_ZYX_1_" + str(shape[0]) + "_" + str(shape[1])


    # zaber_outbound = commands_out2


    ########

    # ibound = str(5000)
    # obound = str(5001)
    # server = str(5002)

    # data_cam = 5003
    # data_stamped = 5005

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

    # job.append(Popen(["lambda_hub",
    #                   "--inbound=L" + obound,
    #                   "--outbound=L" + ibound,
    #                   "--server=" + server,
    #                   "--camera=" + camera,
    #                   "--format=" + fmt,
    #                   "--mode_directory=" + mode_directory]))

    # job.append(Popen(["lambda_client",
    #                   "--port=" + server]))

    # job.append(Popen(["lambda_forwarder",
    #                   "--inbound=" + ibound,
    #                   "--outbound=" + obound]))

    # job.append(Popen(["lambda_logger",
    #                   "--inbound=" + obound,
    #                   "--directory=" + logger_directory]))

    # job.append(Popen(["lambda_dragonfly",
    #                   "--inbound=L" + obound,
    #                   "--outbound=L" + ibound,
    #                   "--port=" + dragonfly_usb_port]))

    # job.append(Popen(["lambda_acquisition_board",
    #                   "--commands_in=L" + obound,
    #                   "--status_out=L" + ibound,
    #                   "--format=" + fmt,
    #                   "--serial_num_daq1=" + serial_num_las_daq,
    #                   "--serial_num_daq0=" + serial_num_cam_daq]))

    # job.append(Popen(["experiment_runner_v2",
    #                   "--inbound=L" + forwarder_out,
    #                   "--outbound=L"+ forwarder_in,
    #                   "--file_directory=C:/src/venkatachalamlab/software/python/vlab/vlab/devices/microfluidics_devices/"]))

    # for i, camera_number in enumerate(cameras):

    #     job.append(Popen(["lambda_displayer",
    #                       "--inbound=L" + str(data_stamped + i),
    #                       "--format=" + fmt,
    #                       "--commands=L" + obound,
    #                       "--name=displayer"+ str(camera_number)]))

    #     job.append(Popen(["lambda_data_hub",
    #                       "--data_in=L" + str(data_cam + i),
    #                       "--commands_in=L" + obound,
    #                       "--data_out=" + str(data_stamped + i),
    #                       "--status_out=L" + ibound,
    #                       "--format=" + fmt,
    #                       "--name=data_hub"+ str(camera_number)]))

    #     job.append(Popen(["lambda_writer",
    #                       "--data_in=L" + str(data_stamped + i),
    #                       "--commands_in=L" + obound,
    #                       "--status_out=L" + ibound,
    #                       "--format=" + fmt,
    #                       "--directory="+ data_directory,
    #                       "--video_name=camera" + str(camera_number),
    #                       "--name=writer"+ str(camera_number)]))

    #     if i == 1:
    #         time.sleep(15)

    #     job.append(Popen(["AndorZylaCamera",
    #                       "--data=*:" + str(data_cam + i),
    #                       "--serial_number=" + serial_number[int(camera_number)-1],
    #                       "--trigger_mode=2",
    #                       "--stack_size=" + str(shape[0]),
    #                       "--y_shape=" + str(shape[1]),
    #                       "--x_shape=" + str(shape[2]),
    #                       "--name=ZylaCamera"+str(camera_number)]))

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







# def Commands(fmt: str,
#              server_port: str,
#              forwarder_outbound_port: str,
#              forwarder_inbound_port: str,
#              camera_data_port: str,
#              processor_inbound_port: str,
#              commands_inbound_port: str,
#              commands_out2: str,
#              image_out: str,
#              system: str):




#     GENERAL_COMMANDS = [


#         ["stage_hub",
#          "--inbound=L"+ forwarder_outbound_port,
#          "--outbound=L" + forwarder_inbound_port,
#          "--format=" + displayer_fmt,
#          "--commands_out2=" + commands_out2,
#          "--server=" + server_port],

#         ["forwarder",
#          "--inbound=" + forwarder_inbound_port,
#          "--outbound=" + forwarder_outbound_port],








    #     ["image_displayer",
    #      "--inbound=L" + camera_data_port,
    #      "--commands=localhost:" + forwarder_outbound_port,
    #      "--format=" +  displayer_fmt,
    #      "--name=image_displayer",
    #      ],

    #     ["image_displayer",
    #      "--inbound=L" + image_out,
    #      "--commands=localhost:" + forwarder_outbound_port,
    #      "--format=" +  displayer_fmt,
    #      "--name=image_displayer",
    #      ],

    #     ["tracker_device",
    #      "--commands_in=L" + forwarder_outbound_port,
    #      "--data_in=L" + camera_data_port,
    #      "--commands_out=L" + forwarder_inbound_port,
    #      "--image_out=" + image_out,
    #      "--format=" + displayer_fmt,
    #      "--system=" + system.lower()],

    #     ["filter",
    #      "--data_in=L" + camera_data_port,
    #      "--commands_in=L" + forwarder_outbound_port,
    #      "--data_out=5009",
    #      "--format=" + filter_fmt,
    #      "--name=filter"],

    #     ["hdf_writer",
    #      "--data_in=localhost:5009",
    #      "--commands_in=localhost:" + forwarder_outbound_port,
    #      "--status_out=localhost:" + forwarder_inbound_port,
    #      "--format=" + displayer_fmt,
    #      "--directory=" + data_path,
    #      "--video_name=data_camera",
    #      "--name=hdf_writer"],

    #     ["FLIRCamera",
    #      "--serial_number=" + serial_number,
    #      "--commands=localhost:" + forwarder_outbound_port,
    #      "--name=camera",
    #      "--data=*:" + camera_data_port,
    #      "--width=" + str(shape[1]),
    #      "--height=" + str(shape[0]),
    #      "--exposure_time=25000"],



    #     ["valve_controller"]

    # ]


    # return GENERAL_COMMANDS


# def run(commands):
#     """This runs all dragonfly system devices."""

#     jobs = []
#     wires = []

#     def finish(*_):

#         for wire in wires:
#             kill(wire.pid, signal.SIGINT)

#         for job in jobs:

#             try:
#                 kill(job.pid, signal.SIGINT)

#             except PermissionError as _e:
#                 print("Received error closing process: ", _e)

#         raise SystemExit

#     signal.signal(signal.SIGINT, finish)

#     for cmd in commands:
#         jobs.append(Popen(cmd))

#     while True:
#         time.sleep(1)




# def main():
#     """CLI entry point."""
#     args = docopt(__doc__)

#     commands = Commands(fmt=args["--format"],
#                         server_port=args["--server_port"],
#                         forwarder_outbound_port=args["--forwarder_outbound_port"],
#                         forwarder_inbound_port=args["--forwarder_inbound_port"],
#                         camera_data_port=args["--camera_data_port"],
#                         processor_inbound_port=args["--processor_inbound_port"],
#                         commands_inbound_port=args["--commands_inbound_port"],
#                         commands_out2=args["--commands_out2"],
#                         image_out=args["--image_out"],
#                         system=args["--system"])


#     run(commands)

# if __name__ == "__main__":
#     main()


