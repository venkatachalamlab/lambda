#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand

"""
This publishes time stamped data.

Usage:
    stage_data_hub.py                         [options]

Options:
    -h --help                           Show this help.
    --data_in=HOST:PORT                 Connection for inbound array data.
                                            [default: L5002]
    --commands_in=HOST:PORT             Connection for commands.
                                            [default: 192.168.170.111:5001]
    --status_out=HOST:PORT              Socket Address to publish status.
                                            [default: 192.168.170.111:5000]
    --data_out=HOST:PORT                Connection for outbound array data.
                                            [default: 5004]
    --format=UINT16_ZYX_20_512_512      Size and type of image being sent. Allowed
                                        values: UINT8_YX_512_512, UINT8_YXC_512_512_3
                                            [default: UINT16_ZYX_25_512_1024]
    --name=NAME                         This name is used for commands subscription.
                                            [default: stage_data_hub]
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

        self.device_status = 1

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
        time.sleep(0.9)
        self.publish_status()

    def set_shape(self, z, y, x):
        """Changes the shape of input and output array."""
        self.shape = (z, y, x)
        self.poller.unregister(self.data_subscriber.socket)

        self.data_publisher.context.term()
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
        self.publish_status()

    def shutdown(self):
        """This Shuts down data hub."""
        self.device_status = 0
        self.publish_status()

    def run(self):
        """This subscribes to images and adds time stamp
         and publish them with TimeStampedPublisher."""
        while self.device_status:

            sockets = dict(self.poller.poll())

            if self.command_subscriber.socket in sockets:
                self.command_subscriber.handle()

            elif self.data_subscriber.socket in sockets:
                self.process()

    def process(self):
        """This subscribes to a volume and publishes that volume to a port"""
        vol = self.data_subscriber.get_last()
        self.data_publisher.send(vol)

    def update_status(self):
        """updates the status dictionary."""
        self.status["shape"] = self.shape
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
