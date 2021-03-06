#! python
#
# Copyright 2021
# Author: Vivek Venkatachalam, Mahdi Torkashvand
#
# This is a convertor of messages from the PROCESSOR
# into stage commands for Zaber stages.
# Author: Vivek Venkatachalam, Mahdi Torkashvand

"""
This converts raw controller output to discrete events.

Usage:
    commands.py             [options]

Options:
    -h --help               Show this help.
    --inbound=HOST:PORT     Connection for inbound messages.
                                [default: L6001]
    --outbound=HOST:PORT    Connection for outbound messages.
                                [default: 6002]
    --console               Stream to stdout.
"""

import time
import signal
from typing import Tuple

import zmq
from docopt import docopt

from lambda_scope.zmq.publisher import Publisher
from lambda_scope.zmq.subscriber import Subscriber
from lambda_scope.zmq.utils import parse_host_and_port

class XboxStageCommands():

    def __init__(self,
                 inbound: Tuple[str, int],
                 outbound: Tuple[str, int]):

        self.subscriber = Subscriber(inbound[1],
                                     inbound[0],
                                     inbound[2])

        self.publisher = Publisher(outbound[1],
                                   outbound[0],
                                   outbound[2])

        buttons = [
            b"X pressed", b"Y pressed", b"B pressed",
            b"A pressed",
            b"dpad_up pressed", b"dpad_up released",
            b"dpad_down pressed", b"dpad_down released",
            b"right_stick", b"left_stick",
            b"left_shoulder pressed", b"right_shoulder pressed"
            ]

        self.subscriber.remove_subscription("")
        for button in buttons:
            self.subscriber.add_subscription(button)

    def run(self):
        tracking = False

        def _finish(*_):
            raise SystemExit

        signal.signal(signal.SIGINT, _finish)

        while True:
            message = self.subscriber.recv_last_string()

            if message is None:
                time.sleep(0.01)
                continue

            tokens = message.split(" ")

            if message in ["X pressed", "B pressed"]:
                if tracking:
                    self.publish("tracker stop")
                    tracking = False
                self.publish("zaber stop_z")
                self.publish("zaber stop_xy")
                self.publish("zaber print_pos")

            elif message == "Y pressed":
                if tracking:
                    self.publish("tracker stop")
                    tracking = False
                self.publish("zaber stop_xy")
                self.publish("zaber home_z")

            elif message == "A pressed":
                if tracking:
                    self.publish("tracker stop")
                    self.publish("zaber stop_xy")
                    tracking = False
                else:
                    self.publish("tracker start")
                    tracking = True

            elif message == "dpad_up pressed":
                self.publish("zaber move_z 1")

            elif message == "dpad_up released":
                self.publish("zaber stop_z")

            elif message == "dpad_down pressed":
                self.publish("zaber move_z -1")

            elif message == "dpad_down released":
                self.publish("zaber stop_z")

            elif message == "left_shoulder pressed":
                self.publish("zaber change_vel_z -1")

            elif message == "right_shoulder pressed":
                self.publish("zaber change_vel_z 1")

            elif tokens[0] == "left_stick":
                xspeed = float(tokens[1]) / 2**15
                yspeed = float(tokens[2]) / 2**15
                self.publish("zaber fine_vel_xy", xspeed, yspeed)

            elif tokens[0] == "right_stick":
                xspeed = float(tokens[1]) / 2**15
                yspeed = float(tokens[2]) / 2**15
                self.publish("zaber coarse_vel_xy", xspeed, yspeed)

            else:
                print("Unexpected message received: ", message)

    def publish(self, verb, *args):
        command = verb
        for arg in args:
            command += " " + str(arg)
        self.publisher.send(command)

def main():
    """CLI entry point."""
    arguments = docopt(__doc__)

    inbound = parse_host_and_port(arguments["--inbound"])
    outbound = parse_host_and_port(arguments["--outbound"])

    processor = XboxStageCommands(inbound, outbound)

    processor.run()

if __name__ == "__main__":
    main()






