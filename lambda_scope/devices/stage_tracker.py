#! python
#
# Copyright 2021
# Authors: Mahdi Torkashvand

"""
This creates a device for the auto tracker

Usage:
    stage_tracker.py                   [options]

Options:
    -h --help                           Show this help.
    --commands_in=HOST:PORT             Host and Port for the incomming commands.
                                            [default: localhost:5001]
    --commands_out=HOST:PORT            Host and Port for the outgoing commands.
                                            [default: localhost:5000]
    --data_in=HOST:PORT                 Host and Port for the incomming image.
                                            [default: localhost:5005]
    --data_out=HOST:PORT                Host and Port for the incomming image.
                                            [default: localhost:5005]
    --format=UINT8_ZYX_1_512_512        Size and type of image being sent.
                                            [default: UINT8_ZYX_1_1200_1920]
"""

import time
import json
from typing import Tuple

import zmq
import cv2
import numpy as np
from docopt import docopt

from lambda_scope.devices.tracker_tools import ObjectDetector, PIDController
from lambda_scope.zmq.array import TimestampedSubscriber, TimestampedPublisher
from lambda_scope.zmq.publisher import Publisher
from lambda_scope.zmq.subscriber import ObjectSubscriber
from lambda_scope.zmq.utils import parse_host_and_port
from lambda_scope.devices.utils import array_props_from_string

class TrackerDevice():
    """This creates a device that subscribes to images from a camera
    and sends commands to the motors"""

    def __init__(
            self,
            commands_in: Tuple[str, int, bool],
            commands_out: Tuple[str, int],
            data_in: Tuple[str, int, bool],
            data_out: Tuple[str, int],
            fmt: str,
            name="tracker"):

        self.status = {}

        self.poller = zmq.Poller()
        self.name = name
        (self.dtype, _, self.shape) = array_props_from_string(fmt)
        self.out = np.zeros(self.shape, dtype=self.dtype)

        self.tracker = ObjectDetector(self.shape)
        self.pid = PIDController(10, 0.0, 0.0,
                                 self.shape[2] // 2, self.shape[1] // 2,
                                 1, 0.025)

        self.camera_number = 1

        self.running = 1
        self.tracking = 0

        self.command_publisher = Publisher(
            host=commands_out[0],
            port=commands_out[1],
            bound=commands_out[2])

        self.data_out = data_out
        self.data_publisher = TimestampedPublisher(
            host=self.data_out[0],
            port=self.data_out[1],
            bound=self.data_out[2],
            shape=self.shape,
            datatype=self.dtype)

        self.command_subscriber = ObjectSubscriber(
            obj=self,
            name=name,
            host=commands_in[0],
            port=commands_in[1],
            bound=commands_in[2])

        self.data_in = data_in
        self.data_subscriber = TimestampedSubscriber(
            host=self.data_in[0],
            port=self.data_in[1],
            bound=self.data_in[2],
            shape=self.shape,
            datatype=self.dtype)

        self.poller.register(self.command_subscriber.socket, zmq.POLLIN)
        self.poller.register(self.data_subscriber.socket, zmq.POLLIN)

        time.sleep(1)
        self.publish_status()

    def set_pid(self, Kp, Ki, Kd):
        self.pid = PIDController(Kp, Ki, Kd,
                                 self.shape[2] // 2, self.shape[1] // 2,
                                 1, 0.025)

    def process(self):
        """This processes the incoming images and sends move commands to zaber."""
        _, data = self.data_subscriber.get_last()

        try:
            self.tracker.get_bbox(data)
        except:
            pass

        p1 = (int(self.tracker.bbox[0]), int(self.tracker.bbox[1]))
        p2 = (int(self.tracker.bbox[0] + self.tracker.bbox[2]),
              int(self.tracker.bbox[1] + self.tracker.bbox[3]))

        img = self.tracker.out.copy()

        cv2.rectangle(img, p1, p2, (255,255,255), 2, 1)
        cv2.circle(img, (self.shape[2] // 2, self.shape[1] // 2), 2, (255, 255, 255), 1)

        self.out[0, ...] = img
        self.data_publisher.send(self.out)

        if self.tracking:
            vel = self.pid.get_velocity(self.tracker.bbox)
            self.command_publisher.send(
                "zaber vel_xy {} {}".format(vel[0], vel[1]))
            self.command_publisher.send("zaber update_position")

    def set_rate(self, rate):
        self.pid.set_rate(rate)

    def set_camera_number(self, camera_number):
        self.camera_number = camera_number
        self.pid.set_camera_number(self.camera_number)
        self.poller.unregister(self.data_subscriber.socket)
        self.data_subscriber.socket.close()

        port = self.data_in[1] + self.camera_number - 1

        self.data_subscriber = TimestampedSubscriber(
            host=self.data_in[0],
            port=port,
            bound=self.data_in[2],
            shape=self.shape,
            datatype=self.dtype)

        self.poller.register(self.data_subscriber.socket, zmq.POLLIN)
        self.publish_status()

    def set_shape(self, z, y ,x):
        self.poller.unregister(self.data_subscriber.socket)

        self.shape = (z, y, x)
        self.tracker.set_shape(z, y, x)
        self.out = np.zeros(self.shape, dtype=self.dtype)

        self.pid.set_center(self.shape[2] // 2, self.shape[1] // 2)

        self.data_subscriber.set_shape(self.shape)
        self.data_publisher.set_shape(self.shape)

        self.poller.register(self.data_subscriber.socket, zmq.POLLIN)
        self.set_crop_size(self.tracker.crop_size)
        self.publish_status()

    def set_feat_size(self, feat_size):
        self.tracker.set_feat_size(feat_size)
        self.publish_status()

    def set_crop_size(self, crop_size):
        self.tracker.set_crop_size(crop_size)
        self.publish_status()

    def stop(self):
        """Stops the subscription to data port."""
        if self.tracking:
            self.tracking = 0
            self.command_publisher.send("zaber stop_xy")
            self.publish_status()

    def start(self):
        """Start subscribing to image data."""
        if not self.tracking:
            self.pid.Ix = 0
            self.pid.Iy = 0
            self.tracking = 1
            self.publish_status()

    def shutdown(self):
        """Shutdown the tracking device."""
        self.stop()
        self.running = 0
        self.publish_status()

    def update_status(self):
        """updates the status dictionary."""
        self.status["shape"] = self.shape
        self.status["tracker_camera_source"] = self.camera_number
        self.status["feature_size"] = self.tracker.feat_size
        self.status["crop_size"] = self.tracker.crop_size
        self.status["tracking"] = self.tracking
        self.status["device"] = self.running


    def publish_status(self):
        """Publishes the status to the hub and logger."""
        self.update_status()
        self.command_publisher.send("hub " + json.dumps({self.name: self.status}, default=int))
        self.command_publisher.send("logger " + json.dumps({self.name: self.status}, default=int))

    def run(self):
        """This subscribes to images and adds time stamp
         and publish them with TimeStampedPublisher."""

        while self.running:

            sockets = dict(self.poller.poll())

            if self.command_subscriber.socket in sockets:
                self.command_subscriber.handle()

            elif self.data_subscriber.socket in sockets:
                self.process()

def main():
    """Create and start auto tracker device."""

    arguments = docopt(__doc__)
    device = TrackerDevice(
        commands_in=parse_host_and_port(arguments["--commands_in"]),
        data_in=parse_host_and_port(arguments["--data_in"]),
        commands_out=parse_host_and_port(arguments["--commands_out"]),
        data_out=parse_host_and_port(arguments["--data_out"]),
        fmt=arguments["--format"])

    device.run()

if __name__ == "__main__":
    main()
