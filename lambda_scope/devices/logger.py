#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand, Vivek Venkatachalam

"""
Logger to save published messages to a file.

Usage:
    logger.py             [options]


Options:
    -h --help              Show this help.
    --inbound=PORT         connecting for inbound messages.
                           [default: 5001]
    --directory=PATH       Location to store published messages.
                           [default: ]
"""

import time

import zmq
from docopt import docopt

from lambda_scope.zmq.utils import get_last
from lambda_scope.devices.utils import make_timestamped_filename

class Logger():
    """This is logger operating on a TCP socket."""

    def __init__(
            self,
            port: int,
            directory: str):

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)

        self.socket.connect("tcp://localhost:{}".format(port))
        self.socket.setsockopt(zmq.SUBSCRIBE, b"logger")

        self.filename = make_timestamped_filename(directory, "log", "txt")
        self.file = open(self.filename, 'w+')

        self.running = False

    def run(self):
        """Subscribes to a string message and writes that on a file."""

        _ = get_last(self.socket.recv_string)
        self.running = True

        while self.running:
            msg = self.socket.recv_string()[7:]
            if msg == "shutdown":
                self.running = False

            msg = self.prepend_timestamp(msg)
            print(msg, file=self.file)

        self.file.close()

    def prepend_timestamp(self, msg: str) -> str:
        """Adds date and time to the string argument."""
        return "{} {}".format(str(time.time()), msg)

def main():
    """main function"""
    args = docopt(__doc__)
    inbound = int(args["--inbound"])
    directory = args["--directory"]

    logger = Logger(inbound, directory)
    logger.run()

if __name__ == "__main__":
    main()
