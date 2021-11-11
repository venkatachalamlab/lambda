#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand, Vivek Venkatachalam

"""
Subscribes to a binary stream over TCP and saves the messages to a file.

Usage:
    writer.py                           [options]

Options:
    -h --help                           Show this help.
    --data_in=HOST:PORT                 Connection for inbound array data.
                                            [default: localhost:5004]
    --commands_in=HOST:PORT             Connection for commands.
                                            [default: localhost:5001]
    --status_out=HOST:PORT              Socket Address to publish status.
                                            [default: localhost:5000]
    --directory=PATH                    Directory to write data to.
                                            [default: ]
    --format=UINT16_ZYX_20_512_512      Size and type of image being sent. Allowed
                                        values: UINT8_YX_512_512, UINT8_YXC_512_512_3
                                            [default: UINT16_ZYX_20_512_1024]
    --saving_mode=mode                  True writes data to file
                                            [default: 0]
    --video_name=NAME                   Directory to write data to.
                                            [default: data]
    --name=NAME                         Device name.
                                            [default: writer]
"""

from typing import Tuple
import multiprocessing
import json
import time

import zmq
from docopt import docopt

from lambda_scope.writers.array_writer import TimestampedArrayWriter
from lambda_scope.zmq.array import TimestampedSubscriber
from lambda_scope.zmq.subscriber import ObjectSubscriber
from lambda_scope.zmq.publisher import Publisher
from lambda_scope.devices.utils import make_timestamped_filename
from lambda_scope.zmq.utils import parse_host_and_port
from lambda_scope.devices.utils import array_props_from_string

class  WriteSession(multiprocessing.Process):
    """This is hdf_writer class"""

    def __init__(
            self,
            data_in: Tuple[str, int],
            commands_in: Tuple[str, int],
            status_out: Tuple[str, int],
            fmt: str,
            saving_mode: str,
            directory: str,
            name="writer",
            video_name="data"):

        multiprocessing.Process.__init__(self)

        self.status = {}
        self.device_status = 1
        self.saving_status = int(saving_mode)
        self.subscription_status = 0

        self.name = name
        self.video_name = video_name

        (self.dtype, _, self.shape) = array_props_from_string(fmt)
        self.file_name = "TBS"
        self.data_in = data_in
        self.directory = directory
        self.poller = zmq.Poller()

        self.status_publisher = Publisher(
            host=status_out[0],
            port=status_out[1],
            bound=status_out[2])

        self.command_subscriber = ObjectSubscriber(
            obj=self,
            name=name,
            host=commands_in[0],
            port=commands_in[1],
            bound=commands_in[2])

        self.data_subscriber = TimestampedSubscriber(
            host=self.data_in[0],
            port=self.data_in[1],
            shape=self.shape,
            datatype=self.dtype,
            bound=self.data_in[2])

        self.poller.register(self.command_subscriber.socket, zmq.POLLIN)
        self.poller.register(self.data_subscriber.socket, zmq.POLLIN)

        time.sleep(1)
        self.publish_status()

    def set_shape(self, z, y, x):
        """Updates the shape, closes the data subscriber, creates a new data subscriber"""
        self.shape = (z, y, x)
        self.poller.unregister(self.data_subscriber.socket)
        self.data_subscriber.set_shape(self.shape)
        self.poller.register(self.data_subscriber.socket, zmq.POLLIN)
        self.publish_status()

    def set_saving_mode(self, saving_mode):
        """Updates the saving mode, 1:ON, 0:OFF"""
        self.saving_status = saving_mode
        self.publish_status()

    def start(self):
        """Registers the data subscriber to the poller."""

        if not self.subscription_status and self.saving_status:
            self.filename = make_timestamped_filename(self.directory,
                                                      self.video_name, "h5")

            self.writer = TimestampedArrayWriter.from_source(self.data_subscriber,
                                                             self.filename)
            self.subscription_status = 1
            self.publish_status()

    def stop(self):
        """Closes the hdf file, updates the status. """
        if self.subscription_status:
            self.subscription_status = 0
            self.writer.close()
            self.publish_status()

    def shutdown(self):
        """Close the hdf file and end while true loop of the poller"""
        self.stop()
        self.device_status = 0
        self.publish_status()

    def run(self):
        """Start a while true loop with a poller that has command_subscriber already registered."""

        while self.device_status:

            sockets = dict(self.poller.poll())

            if self.command_subscriber.socket in sockets:
                self.data_subscriber.get_last()
                self.command_subscriber.handle()


            if self.subscription_status:
                if self.data_subscriber.socket in sockets:
                    self.writer.save_frame()


    def update_status(self):
        """Updates the status dictionary."""
        self.status["shape"] = self.shape
        self.status["saving"] = self.saving_status
        self.status["running"] = self.subscription_status
        self.status["device"] = self.device_status

    def publish_status(self):
        """Publishes the status to the hub and logger."""
        self.update_status()
        self.status_publisher.send("hub " + json.dumps({self.name: self.status}, default=int))
        self.status_publisher.send("logger "+ json.dumps({self.name: self.status}, default=int))


def main():
    """CLI entry point."""

    args = docopt(__doc__)

    writer = WriteSession(
        data_in=parse_host_and_port(args["--data_in"]),
        commands_in=parse_host_and_port(args["--commands_in"]),
        status_out=parse_host_and_port(args["--status_out"]),
        fmt=args["--format"],
        saving_mode=args["--saving_mode"],
        directory=args["--directory"],
        name=args["--name"],
        video_name=args["--video_name"])

    writer.run()

if __name__ == "__main__":
    main()
