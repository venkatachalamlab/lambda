#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand

"""
This controls interval imaging, and publishes time stamped data.

Usage:
    data_hub.py                         [options]

Options:
    -h --help                           Show this help.
    --data_in=HOST:PORT                 Connection for inbound array data.
                                            [default: L5001]
    --commands_in=HOST:PORT             Connection for commands.
                                            [default: L5002]
    --status_out=HOST:PORT              Socket Address to publish status.
                                            [default: L5003]
    --data_out=HOST:PORT                Connection for outbound array data.
                                            [default: 5004]
    --format=UINT16_ZYX_20_512_512      Size and type of image being sent. Allowed
                                        values: UINT8_YX_512_512, UINT8_YXC_512_512_3
                                            [default: UINT16_ZYX_25_512_1024]
    --name=NAME                         This name is used for commands subscription.
                                            [default: data_hub]
"""

import time
import json
from typing import Tuple

import zmq
import numpy as np
from docopt import docopt

from lambda_scope.zmq.publisher import Publisher
from lambda_scope.zmq.subscriber import ObjectSubscriber
from lambda_scope.zmq.array import TimestampedPublisher, Subscriber
from lambda_scope.devices.utils import array_props_from_string
from lambda_scope.zmq.utils import parse_host_and_port

class DataHub():

    def __init__(
            self,
            data_in: Tuple[str, int, bool],
            commands_in: Tuple[str, int, bool],
            data_out: Tuple[str, int, bool],
            status_out: Tuple[str, int],
            fmt: str,
            name: str):

        self.status = {}
        self.name = name

        self.data_in = data_in
        self.data_out = data_out

        self.resting_time = 0
        self.taken_volumes = 0
        self.device_status = 1
        self.imaging_volumes = 1
        self.subscription_status = 0
        self.interruption_status = 0

        (self.dtype, _, self.shape) = array_props_from_string(fmt)

        self.poller = zmq.Poller()

        self.command_subscriber = ObjectSubscriber(
            obj=self,
            name=name,
            host=commands_in[0],
            port=commands_in[1],
            bound=commands_in[2])

        self.publisher = Publisher(
            host=status_out[0],
            port=status_out[1],
            bound=status_out[2])

        self.data_publisher = TimestampedPublisher(
            host=self.data_out[0],
            port=self.data_out[1],
            datatype=self.dtype,
            shape=self.shape,
            bound=self.data_out[2])

        self.data_subscriber = Subscriber(
            host=self.data_in[0],
            port=self.data_in[1],
            datatype=self.dtype,
            shape=self.shape,
            bound=self.data_in[2])

        self.poller.register(self.command_subscriber.socket, zmq.POLLIN)
        self.poller.register(self.data_subscriber.socket, zmq.POLLIN)
        self.publish_status()

    def set_shape(self, z, y, x):
        """Changes the shape of input and output array."""
        self.shape = (z, y, x)
        self.poller.unregister(self.data_subscriber.socket)

        self.data_publisher.socket.close()
        self.data_subscriber.socket.close()

        self.data_publisher = TimestampedPublisher(
            host=self.data_out[0],
            port=self.data_out[1],
            datatype=self.dtype,
            shape=self.shape,
            bound=self.data_out[2])

        self.data_subscriber = Subscriber(
            host=self.data_in[0],
            port=self.data_in[1],
            datatype=self.dtype,
            shape=self.shape,
            bound=self.data_in[2])

        self.poller.register(self.data_subscriber.socket, zmq.POLLIN)
        time.sleep(0.9)
        self.publish_status()

    def set_timer(self, nvolumes, off_time):
        """Sets new values for the imaging times."""
        self.imaging_volumes = nvolumes
        self.resting_time = off_time
        self.publish_status()

    def start(self):
        """Start subscribing to image data."""
        if not self.subscription_status:
            self.subscription_status = 1
            self.publish_status()

    def stop(self):
        """Stop stacking and discard any unfinished stacked image"""
        if self.subscription_status:
            self.subscription_status = 0
            self.taken_volumes = 0
            self.interruption_status = 0
            self.publish_status()

    def shutdown(self):
        """This Shuts down data hub."""
        self.stop()
        self.device_status = 0
        self.publish_status()

    def run(self):
        """This subscribes to images and adds time stamp
         and publish them with TimeStampedPublisher."""
        while self.device_status:

            sockets = dict(self.poller.poll())

            if self.command_subscriber.socket in sockets:
                self.command_subscriber.handle()


            if self.subscription_status:
                if self.data_subscriber.socket in sockets:
                    self.process()

    def process(self):
        """This subscribes to a volume and publishes that volume to a port"""
        vol = self.data_subscriber.get_last()

        if self.resting_time == 0:
            self.data_publisher.send(vol)
        else:
            if self.taken_volumes < self.imaging_volumes:
                self.data_publisher.send(vol)
                self.taken_volumes += 1
                # if self.taken_volumes >= 120 and self.taken_volumes < 240:
                #     if self.taken_volumes % 8 <= 3:
                #         self.command_publisher.send("hub _daq_set_green_led 1")
                #     elif self.taken_volumes % 8 > 3:
                #         self.command_publisher.send("hub _daq_set_green_led 0")
                # else:
                #     self.command_publisher.send("hub _daq_set_green_led 0")

                # if self.taken_volumes == 80:
                #     self.publisher.send("hub _daq_stop_green")

            elif self.taken_volumes == self.imaging_volumes:
                print("Session Ended.")
                self.interrupt()

    def interrupt(self):
        """Stops daq devices, wait for specified amount of time and then runs them
        again"""
        self.interruption_status = 1
        self.taken_volumes = 0
        daq_stop = 0
        cam_start = 0

        t0 = time.time()
        self.publisher.send("hub _camera_stop")
        self.publisher.send("hub _daq_laser_stop")

        while self.interruption_status:
            t = time.time() - t0

            if not daq_stop and t >= 0.5:
                self.publisher.send("hub _daq_stop")
                daq_stop = 1

            elif not cam_start and t >= (self.resting_time-0.5):
                self.publisher.send("hub _camera_start")
                cam_start = 1

            elif t >= self.resting_time:
                self.publisher.send("hub _daq_start")
                self.interruption_status = 0
                self.data_subscriber.get_last()
                print("Session Started.")
                break

            sockets = dict(self.poller.poll())
            if self.command_subscriber.socket in sockets:
                self.data_subscriber.get_last()
                self.command_subscriber.handle()

    def update_status(self):
        """updates the status dictionary."""
        self.status["shape"] = self.shape
        self.status["total_volume"] = self.imaging_volumes
        self.status["rest_time"] = self.resting_time
        self.status["running"] = self.subscription_status
        self.status["device"] = self.device_status


    def publish_status(self):
        """Publishes the status to the hub and logger."""
        self.update_status()
        self.publisher.send("hub " + json.dumps({self.name: self.status}, default=int))
        self.publisher.send("logger " + json.dumps({self.name: self.status}, default=int))

def main():
    """CLI entry point."""

    args = docopt(__doc__)

    device = DataHub(
        data_in=parse_host_and_port(args["--data_in"]),
        commands_in=parse_host_and_port(args["--commands_in"]),
        data_out=parse_host_and_port(args["--data_out"]),
        status_out=parse_host_and_port(args["--status_out"]),
        fmt=args["--format"],
        name=args["--name"])

    device.run()

if __name__ == "__main__":
    main()
