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

        
        self.shuffled_odor_valves = []
        self.shuffled_odor_names = []
        self.odor_valves = [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.odor_names = [
            "Fluorescein",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
        ]
        self.randomized = 1
        self.cycle = 1
        self.initial_time = 60
        self.buffer_time = 30
        self.odor_time = 15
        self.buffer_valve = 1
        self.control1_valve = 2
        self.control2_valve = 3
        self.control1_name = ""
        self.control2_name = ""
        self.buffer_name = ""
        self.status = {}
        self.valves = []
        self.current_valves = []
        self.times = []
        self.flow = []

        self.temp_valves = []
        self.temp_names = []

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

        self.status["odor_valves"] = self.odor_valves
        self.status["odor_names"] = self.odor_names
        self.status["randomized"] = self.randomized
        self.status["cycle"] = self.cycle
        self.status["initial_time"] = self.initial_time
        self.status["buffer_time"] = self.buffer_time
        self.status["odor_time"] = self.odor_time
        self.status["buffer_valve"] = self.buffer_valve
        self.status["control1_valve"] = self.control1_valve
        self.status["control2_valve"] = self.control2_valve
        self.status["control1_name"] = self.control1_name
        self.status["control2_name"] = self.control2_name
        self.status["buffer_name"] = self.buffer_name
        self.status["flow"] = ""
        self.prepare()
        time.sleep(1)
        self.publish_status()

    def set_odor_valve(self, idx, valve_number):
        self.odor_valves[idx] = valve_number
        self.status["odor_valves"] = self.odor_valves
        self.prepare()
        self.publish_status()
    
    def set_odor_name(self, *args):
        idx = args[0]
        name = " ".join(map(str, args[1:]))
        if name == "none":
            self.odor_names[idx] = ""
        else:
            self.odor_names[idx] = name
        self.status["odor_names"] = self.odor_names
        self.prepare()
        self.publish_status()

    def set_randomness(self, is_random):
        self.randomized = is_random
        self.status["randomized"] = self.randomized
        self.prepare()
        self.publish_status()

    def set_cycle(self, cycle):
        self.cycle = cycle
        self.status["cycle"] = self.cycle
        self.prepare()
        self.publish_status()

    def set_initial_time(self, initial_time):
        self.initial_time = initial_time
        self.status["initial_time"] = self.initial_time
        self.prepare()
        self.publish_status()

    def set_buffer_time(self, buffer_time):
        self.buffer_time = buffer_time
        self.status["buffer_time"] = self.buffer_time
        self.prepare()
        self.publish_status()

    def set_buffer_name(self, *args):
        buffer_name = " ".join(args)
        if buffer_name == "none":
            self.buffer_name = ""
        else:
            self.buffer_name = buffer_name
        self.status["buffer_name"] = self.buffer_name
        self.prepare()
        self.publish_status()

    def set_odor_time(self, odor_time):
        self.odor_time = odor_time
        self.status["odor_time"] = self.odor_time
        self.prepare()
        self.publish_status()

    def set_buffer_valve(self, buffer_valve):
        self.buffer_valve = buffer_valve
        self.status["buffer_valve"] = self.buffer_valve
        self.prepare()
        self.publish_status()

    def set_control1_valve(self, control1_valve):
        self.control1_valve = control1_valve
        self.status["control1_valve"] = self.control1_valve
        self.prepare()
        self.publish_status()

    def set_control2_valve(self, control2_valve):
        self.control2_valve = control2_valve
        self.status["control2_valve"] = self.control2_valve
        self.prepare()
        self.publish_status()

    def set_control1_name(self, *args):
        control1_name = " ".join(map(str, args))
        if control1_name  == "none":
            self.control1_name = ""
        else:
            self.control1_name = control1_name
        self.status["control1_name"] = self.control1_name
        self.prepare()
        self.publish_status()

    def set_control2_name(self, *args):
        control2_name = " ".join(map(str, args))
        if control2_name  == "none":
            self.control2_name = ""
        else:
            self.control2_name = control2_name
        self.status["control2_name"] = self.control2_name
        self.prepare()
        self.publish_status()

    def _get_odor_sequence(self):
        self.temp_valves = []
        self.temp_names = []
        for i, valve_number in enumerate(self.odor_valves):
            if valve_number !=0:
                self.temp_valves.append(valve_number)
                self.temp_names.append(self.odor_names[i])

        temp = self.temp_valves.copy()
        if self.randomized in (1, "1", True, "true", "True"):
            random.shuffle(temp)
        index = [self.temp_valves.index(odor) for odor in temp]
        self.shuffled_odor_valves = self.cycle * temp
        self.shuffled_odor_names = self.cycle * [self.temp_names[i] for i in index]


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

        self.status["flow"] = self.flow[counter]
        self.publish_status()

    def publish_status(self):
        "publish device status"
        self.status["time"] = time.time()
        self.publisher.send("hub " + json.dumps({self.name: self.status}, default=int))
        self.publisher.send("logger "+ json.dumps({self.name: self.status}, default=int))

    def prepare(self):
        self._get_odor_sequence()
        self._make_intervals()

    def start(self):
        if not self.running:
            self.running = True
            self._loop()

    def stop(self):
        if self.running:
            self.running = False
            self._publish(-1)
            self.prepare()
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
