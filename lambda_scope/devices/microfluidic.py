#! python
#
# Copyright 2021
# Author: Maedeh Seyedolmohadesin, Mahdi Torkashvand

"""
This creates a microfluidics device.

Usage:
    microfluidic.py              [options]

Options:
    -h --help                    Show this help.
    --inbound=HOST:PORT          Socket address to receive messages.
                                  [default: L5001]
    --outbound=HOST:PORT         Socket address to publish messages.
                                  [default: L5000]
"""

import time
import json
import random
import threading
from typing import Tuple

import numpy as np
from docopt import docopt

from lambda_scope.zmq.utils import parse_host_and_port
from lambda_scope.zmq.subscriber import ObjectSubscriber
from lambda_scope.zmq.publisher import Publisher

class MicrofluidicDevice:
    """ this runs a microfluidics experiment"""

    def __init__(self,
                 outbound: Tuple[str, int, bool],
                 inbound: Tuple[str, int, bool],
                 name="microfluidic_device"):
        self.device_running = True
        self.running = False
        self.name = name

        self.odor_valves = [4, 6, 9, 10, 11, 12, 13, 14, 15, 16]
        self.shuffled_odor_valves = []
        self.odor_names = [
            "Fluorescein",
            "10mM CuSO4",
            "Control",
            "800mM Sorbitol",
            "1uM ascr#3",
            "OP50",
            "e-2 IAA",
            "e-6 IAA",
            "450mM NaCl",
            "75mM NaCl"
        ]
        self.shuffled_odor_names = []
        self.randomized = True
        self.cycle = 2
        self.initial_time = 10
        self.buffer_time = 5
        self.odor_time = 3
        self.buffer_valve = 1
        self.control1_valve = 2
        self.control2_valve = 3
        self.buffer_name = "hi"
        self.status = {}
        self.valves = []
        self.current_valves = []
        self.times = []
        self.flow = []

        self.command_subscriber = ObjectSubscriber(
            obj=self,
            name=name,
            host=inbound[0],
            port=inbound[1],
            bound=inbound[2])

        self.publisher = Publisher(
            host=outbound[0],
            port=outbound[1],
            bound=outbound[2])

    def _get_odor_sequence(self):
        temp = self.odor_valves.copy()
        if self.randomized == True:
            random.shuffle(temp)
        index = [self.odor_valves.index(odor) for odor in temp]
        self.shuffled_odor_valves = self.cycle * temp
        self.shuffled_odor_names = self.cycle * [self.odor_names[i] for i in index]


    def _make_intervals(self):
        number_of_odors = len(self.shuffled_odor_valves)
        self.valves = np.full((17, 3*(number_of_odors)+2), 0)
        self.times = np.full((3*(number_of_odors)+2,), 0)
        self.flow = (3*number_of_odors+2) * [""]

        self.times[0] = 0
        self.times[1] = self.initial_time

        self.valves[self.buffer_valve, :] = 1

        self.valves[self.control1_valve, 0] = 1
        self.valves[self.shuffled_odor_valves[0], 0] = 1

        self.flow[0]= self.flow[-1] = self.buffer_name

        self.valves[self.control1_valve, -1] = 1
        self.valves[self.control2_valve, -1] = 1

        for i in range(number_of_odors):

            self.valves[self.control2_valve, (3*i)+1] = 1
            self.valves[self.shuffled_odor_valves[i], (3*i)+1] = 1
            self.times[3*i+2] = self.odor_time + self.times[3*i+1]
            self.flow[(3*i)+1] = self.shuffled_odor_names[i]

            self.valves[self.control1_valve, (3*i)+2] = 1
            self.valves[self.shuffled_odor_valves[i], (3*i)+2] = 1
            self.times[3*i+3] = 2 + self.times[3*i+2]
            self.flow[(3*i)+2] = self.buffer_name

            self.valves[self.control1_valve, (3*i)+3] = 1
            self.valves[self.shuffled_odor_valves[(i+1)%number_of_odors], (3*i)+3] = 1
            self.times[3*i+4] = self.buffer_time - 2 + self.times[3*i+3]
            self.flow[(3*i)+3] = self.buffer_name

        self.valves = self.valves[1:, :]

    def _make_valve_names(self):
        valve_names = [""]*17
        valve_names[self.buffer_valve] = self.buffer_name
        valve_names[self.control1_valve] = "control1"
        valve_names[self.control2_valve] = "control2"
        counter = 0
        for odor in self.odor_valves:
            valve_names[odor] = self.odor_names[counter]
            counter += 1

        self.status["valve_names"] = list(valve_names[1:])
        return valve_names[1:]

    def _loop(self):
        t0 = time.time()
        counter = 0
        while self.running:
            dt = time.time()-t0
            if dt > self.times[counter]:
                self._publish(counter)
                counter += 1
            if counter == self.times.shape[0]:
                self.running = 0
            msg = self.command_subscriber.recv_last()
            if msg:
                self.command_subscriber.process(msg)
        self.publisher.send("hub stop")

    def _publish(self, counter):
        for i, element in enumerate(self.valves[:, counter]):
            self.publisher.send("valve switch_valve {} {}".format(i, element))

        self.status["valve_status"] = list(self.valves[:, counter])
        self.status["flow"] = self.flow[counter]
        self.publish_status()

    def publish_status(self):
        "publish device status"
        self.status["time"] = time.time()
        self.publisher.send("hub " + json.dumps({self.name: self.status}, default=int))
        self.publisher.send("logger "+ json.dumps({self.name: self.status}, default=int))


    def start(self):
        if not self.running:
            self.running = True
            self._get_odor_sequence()
            self._make_intervals()
            self._make_valve_names()
            self._loop()

    def stop(self):
        if self.running:
            self.running = False
            self._publish(-1)
            self.publisher.send("hub stop")

    def run(self):
        while self.device_running:
            self.command_subscriber.handle()

    def shutdown(self):
        self.stop()
        self.device_running = False

def main():
    """Create and start an ExperimentRunner Device object."""

    arguments = docopt(__doc__)

    device = MicrofluidicDevice(
        inbound=parse_host_and_port(arguments["--inbound"]),
        outbound=parse_host_and_port(arguments["--outbound"])
    )

    device.run()


if __name__ == "__main__":
    main()
