#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand, Vivek Venkatachalam

"""
This subscribes to a binary stream bound to a socket and displays each message
as an image.

Usage:
    displayer.py                    [options]

Options:
    -h --help                       Show this help.
    --inbound=HOST:PORT             Connection for inbound messages.
                                        [default: L5005]
    --commands=HOST:PORT            Connection to recieve messages.
                                        [default: L5001]
    --format=UINT16_ZYX_25_512_512  Size and type of image being sent.
                                        [default: UINT16_ZYX_25_512_1024]
    --name=STRING                   Name of image window.
                                        [default: displayer]
    --lookup_table=213_2004         Lookup table.
                                        [default: 0_255]
"""

from typing import Optional, Tuple

import cv2
import zmq
import numpy as np
from docopt import docopt

from lambda_scope.zmq.utils import parse_host_and_port
from lambda_scope.zmq.subscriber import ObjectSubscriber
from lambda_scope.zmq.array import TimestampedSubscriber
from lambda_scope.devices.utils import array_props_from_string

class Displayer:
    """This creates a displayer with 2 subscribers, one for images
    and one for commands."""
    def __init__(
            self,
            inbound: Tuple[str, int],
            commands: Tuple[str, int, bool],
            fmt: str,
            name: str,
            lookup_table: Optional[Tuple[int, int]]):

        (self.dtype, _, self.shape) = array_props_from_string(fmt)
        self.mip_image = np.zeros((self.shape[1] + 4 * self.shape[0],
                                   self.shape[2] + 4 * self.shape[0]), self.dtype)
        self.dtype_max = np.iinfo(self.dtype).max
        self.displayer_shape = self.mip_image.shape

        self.name = name
        self.running = True
        self.inbound = inbound
        self.lookup_table = lookup_table

        self.command_subscriber = ObjectSubscriber(
            obj=self,
            name=name,
            host=commands[0],
            port=commands[1],
            bound=commands[2])

        self.data_subscriber = TimestampedSubscriber(
            host=self.inbound[0],
            port=self.inbound[1],
            shape=self.shape,
            datatype=self.dtype,
            bound=self.inbound[2])

        cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.name, self.displayer_shape[1], self.displayer_shape[0])

        self.set_lookup_table(lookup_table[0], lookup_table[1])

    def set_lookup_table(self, lut_low, lut_high):
        if lut_high > self.dtype_max:
            self.lookup_table = (0, self.dtype_max)
        else:
            self.lookup_table = (lut_low, lut_high)
        self.scale = int(np.floor(self.dtype_max / (self.lookup_table[1] - self.lookup_table[0])))

    def set_shape(self, z, y, x):
        self.data_subscriber.socket.close()

        self.shape = (z, y, x)

        self.data_subscriber = TimestampedSubscriber(
            host=self.inbound[0],
            port=self.inbound[1],
            shape=self.shape,
            datatype=self.dtype,
            bound=self.inbound[2])

        self.mip_image = np.zeros((self.shape[1] + 4 * self.shape[0],
                                   self.shape[2] + 4 * self.shape[0]), self.dtype)
        self.displayer_shape = self.mip_image.shape

        cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.name, self.displayer_shape[1], self.displayer_shape[0])



    def process(self):
        msg = self.data_subscriber.get_last()

        if msg is not None:
            mip_z = np.max(msg[1], axis=0)
            mip_y = np.max(msg[1], axis=1)
            mip_x = np.max(msg[1], axis=2)


            scaled_mip_y = np.repeat(mip_y, 4, axis=0)
            scaled_mip_x = np.repeat(mip_x, 4, axis=0)
            t_scaled_mip_x = np.transpose(scaled_mip_x)

            self.mip_image[:self.shape[1], :self.shape[2]] = mip_z
            self.mip_image[:self.shape[1], self.shape[2]:] = t_scaled_mip_x
            self.mip_image[self.shape[1]:, :self.shape[2]] = scaled_mip_y

            self.mip_image = np.clip(self.mip_image,
                                     self.lookup_table[0],
                                     self.lookup_table[1])
            self.mip_image = self.mip_image - self.lookup_table[0]
            self.mip_image = (self.mip_image * self.scale).astype(np.uint8)
        else:
            self.mip_image = np.zeros_like(self.mip_image, dtype=np.uint8)

        cv2.imshow(self.name, self.mip_image)
        cv2.waitKey(1)

    def run(self):
        while self.running:
            command = self.command_subscriber.recv_last()
            if command:
                self.command_subscriber.process(command)
            else:
                self.process()

    def shutdown(self):
        self.running = False

def main():
    """CLI entry point."""

    args = docopt(__doc__)

    lookup_table = args["--lookup_table"]
    if lookup_table is not None:
        lookup_table = tuple(map(int, lookup_table.split("_")))


    device = Displayer(inbound=parse_host_and_port(args["--inbound"]),
                       commands=parse_host_and_port(args["--commands"]),
                       fmt=args["--format"],
                       name=args["--name"],
                       lookup_table=lookup_table)

    device.run()

if __name__ == "__main__":
    main()
