#! python
#
# Copyright 2021
# Author: Vivek Venkatachalam, Mahdi Torkashvand
#
# This is a consumer of raw messages from an XINPUT device. Messages are
# obtained from a ZMQ PUB socket. They are then processed to determine whether
# a button was hit or released, or whether an analog trigger/joystick is
# outside its deadzone.
#
# The input message follows the structure of _XINPUT_GAMEPAD from MSDN:
#
#       typedef struct _XINPUT_GAMEPAD {
#         WORD  wButtons;
#         BYTE  bLeftTrigger;
#         BYTE  bRightTrigger;
#         SHORT sThumbLX;
#         SHORT sThumbLY;
#         SHORT sThumbRX;
#         SHORT sThumbRY;
#       } XINPUT_GAMEPAD, *PXINPUT_GAMEPAD;
#
# The output messages are ASCII encoded and of the form:
#
#       "A pressed"
#       "A released"
#       "dpad_right pressed"
#       "left_thumb released"
#       "left_stick -15344 0"
#       "left_trigger 255"
#
# Buttons (X, Y, A, B, start, back, left shoulder, and right shoulder) will
# emit events when pressed and when released.

"""
This XInput processor converts raw controller output to discrete events.

Usage:
    processor.py           [options]

Options:
    -h --help               Show this help.
    --inbound=HOST:PORT     Connection for inbound messages.
                                [default: L6000]
    --outbound=HOST:PORT    Binding for outbound messages.
                                [default: 6001]
    --deadzone=DEADZONE     Thumbstick deadzone.
                                [default: 3000]
    --threshold=THRESHOLD   Trigger activation threshold.
                                [default: 30]
    --console               Stream to stdout.
"""

import struct
import signal
import time
from typing import List, Tuple
from collections import namedtuple

import zmq
from docopt import docopt

from lambda_scope.zmq.publisher import Publisher
from lambda_scope.zmq.subscriber import Subscriber
from lambda_scope.zmq.utils import parse_host_and_port

GamepadState = namedtuple(
    "GamepadState",
    [
        "dpad_up",
        "dpad_down",
        "dpad_left",
        "dpad_right",
        "start",
        "back",
        "left_thumb",
        "right_thumb",
        "left_shoulder",
        "right_shoulder",
        "A",
        "B",
        "X",
        "Y",
        "left_trigger",
        "right_trigger",
        "left_stick",
        "right_stick"
    ])

GamepadButtonMask = {
    "dpad_up"       : 0x0001,
    "dpad_down"     : 0x0002,
    "dpad_left"     : 0x0004,
    "dpad_right"    : 0x0008,
    "start"         : 0x0010,
    "back"          : 0x0020,
    "left_thumb"    : 0x0040,
    "right_thumb"   : 0x0080,
    "left_shoulder" : 0x0100,
    "right_shoulder": 0x0200,
    "A"             : 0x1000,
    "B"             : 0x2000,
    "X"             : 0x4000,
    "Y"             : 0x8000
}

def get_last(receiver):
    """This retrieves the most recent message sent to a socket using
    func. If no messages are available, this will return None."""

    msg = None

    while True:
        try:
            msg = receiver(flags=zmq.NOBLOCK)
        except zmq.error.Again:
            break
        except:
            raise

    return msg

class XInputProcessor():

    def __init__(self,
                 inbound: Tuple[str, int],
                 outbound: Tuple[str, int],
                 thumbstick_deadzone: int,
                 trigger_threshold: int,
                 stream_to_console=False):

        self.thumbstick_deadzone = thumbstick_deadzone
        self.trigger_threshold = trigger_threshold
        self.stream_to_console = stream_to_console

        self.current_state = GamepadState(
            *([False]*14), 0, 0, (0, 0), (0, 0))

        self.subscriber = Subscriber(inbound[1],
                                     inbound[0],
                                     inbound[2])
                    
        self.publisher = Publisher(outbound[1],
                                   outbound[0],
                                   outbound[2])

    def run(self):
        """This runs the processor."""

        signal.signal(signal.SIGINT, self.shutdown)

        while True:
            raw = get_last(self.subscriber.recv)

            if raw is None:
                time.sleep(0.001)
                continue

            new_state = self.sanitize_state(self.gamepad_state_from_bytes(raw))

            messages = self.get_events_from_states(self.current_state, new_state)

            for msg in messages:
                self.publisher.send(msg)

                if self.stream_to_console:
                    print(msg)

            self.current_state = new_state

    def shutdown(self, *_):
        """This terminates the processor."""
        print("Xinput Processor: Shutting down.")
        raise SystemExit

    @staticmethod
    def gamepad_state_from_bytes(msg: bytes) -> GamepadState:
        """This converts a sequence of bytes into a valid GamepadState."""

        vals = struct.unpack(b'HBBhhhh', msg)

        # Handle the buttons.
        state_dict = {}
        for b, mask in GamepadButtonMask.items():
            state_dict[b] = bool(vals[0] & mask)

        # Handle the triggers.
        state_dict["left_trigger"] = vals[1]
        state_dict["right_trigger"] = vals[2]

        # Handle the sticks.
        state_dict["left_stick"] = (vals[3], vals[4])
        state_dict["right_stick"] = (vals[5], vals[6])

        return GamepadState(**state_dict)



    def sanitize_state(self, s: GamepadState) -> GamepadState:
        """This takes a gamepad state and determines whether the analog signals
        are above the required thresholds. A new sanitized state is
        returned."""

        thresh = self.trigger_threshold
        clean_trigger = lambda x: x if x >= thresh else 0

        left_trigger = clean_trigger(s.left_trigger)
        right_trigger = clean_trigger(s.right_trigger)

        dzone = self.thumbstick_deadzone
        clean_stick_xy = lambda x: x if abs(x) >= dzone else 0
        clean_stick = lambda x: tuple(map(clean_stick_xy, x))

        left_stick = clean_stick(s.left_stick)
        right_stick = clean_stick(s.right_stick)

        return GamepadState(*s[0:14], left_trigger, right_trigger, left_stick,
           right_stick)

    @staticmethod
    def get_events_from_states(s0: GamepadState, s1: GamepadState)->List[str]:
        """This calculates the difference between two controller states and
        generates a list of events  describing the difference."""

        messages =[]

        # Handle the buttons.
        for b in GamepadButtonMask:
            v1 = getattr(s1, b)
            v0 = getattr(s0, b)
            if v1 > v0:
                messages.append("{} pressed".format(b))
            elif v1 < v0:
                messages.append("{} released".format(b))

        # Handle the triggers.
        if s1.left_trigger != s0.left_trigger:
            messages.append("left_trigger {}".format(s1.left_trigger))
        if s1.right_trigger != s0.right_trigger:
            messages.append("right_trigger {}".format(s1.right_trigger))

        # Handle the thumbsticks.
        if s1.left_stick != s0.left_stick:
            messages.append(
                "left_stick {} {}".format(*s1.left_stick))

        if s1.right_stick != s0.right_stick:
            messages.append(
                "right_stick {} {}".format(*s1.right_stick))

        return messages

def main():
    """CLI entry point."""

    arguments = docopt(__doc__)

    inbound = parse_host_and_port(arguments["--inbound"])
    outbound = parse_host_and_port(arguments["--outbound"])
    deadzone = int(arguments["--deadzone"])
    threshold = int(arguments["--threshold"])

    console = bool(arguments["--console"])

    processor = XInputProcessor(inbound, outbound, deadzone, threshold, console)

    processor.run()

if __name__ == "__main__":
    main()
