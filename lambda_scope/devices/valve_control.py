#! python
#
# Copyright 2021
# Author: Maedeh Seyedolmohadesin, Mahdi Torkashvand

"""
This creates a Microfluidics device.

Usage:
    valve_control.py              [options]

Options:
    -h --help                     Show this help.
    --commands=HOST:PORT          Socket address to receive messages.
                                  [default: 192.168.170.111:5001]
    --status=HOST:PORT            Socket address to publish messages.
                                  [default: 192.168.170.111:5000]

"""

from __future__ import absolute_import, division, print_function
import json
import time
from typing import Tuple

import nidaqmx
import numpy as np
from docopt import docopt
from nidaqmx.constants import LineGrouping

from lambda_scope.zmq.subscriber import ObjectSubscriber
from lambda_scope.zmq.publisher import Publisher
from lambda_scope.zmq.utils import parse_host_and_port

class ValveController():
    """This is a DAQ device that subscribes from message forwarder"""

    def __init__(
            self,
            status: Tuple[str, int, bool],
            commands: Tuple[str, int, bool],
            name="valve"):

        self.name = name
        self.status = np.full((16), False, dtype=bool)
        self.msg_status = ""
        self.stop_flag = False

        self.command_subscriber = ObjectSubscriber(
            obj=self,
            name=name,
            host=commands[0],
            port=commands[1],
            bound=commands[2])

        self.status_publisher = Publisher(
            host=status[0],
            port=status[1],
            bound=status[2])

    def _valve_encode(self):
        valve_array = np.full((16), 0)
        valve_array[self.status] = 1
        return valve_array

    def _valve_decode(self, status_int):
        status_string = str(status_int)[1:]
        current_status = np.full((16), False)
        for i in range(16):
            if status_string[i] == "1":
                current_status[i] = True
        return current_status

    def _update_status(self, current_status):
        self.status = current_status
        self._set_valves()
        self.publish_status()
        print(str(self._valve_encode()))

    def publish_status(self):
        status = {}
        status["time"] = time.time()
        status["valve_status"] = list(self.status)
        self.status_publisher.send("hub " +json.dumps({self.name: status}, default=int))
        self.status_publisher.send("logger " +json.dumps({self.name: status}, default=int))

    def _set_valves(self):
        """set the valves through DAQ """
        with nidaqmx.Task("Read_Output1") as task:
            task.do_channels.add_do_chan('Dev2/port0/line0:7',
                                         line_grouping=LineGrouping.CHAN_PER_LINE)

            task.do_channels.add_do_chan('Dev2/port2/line0:3',
                                         line_grouping=LineGrouping.CHAN_PER_LINE)

            task.do_channels.add_do_chan('Dev2/port1/line4:7',
                                         line_grouping=LineGrouping.CHAN_PER_LINE)
            task.write(self.status)

    def switch_valve(self, valve_num, status):
        """switches only one valve"""
        current_status = np.copy(self.status)
        if status in ("1", 1, True, "True"):
            current_status[valve_num] = True
        elif status in ("0", 0, False, "False"):
            current_status[valve_num] = False
        self._update_status(current_status)

    def switch_valves(self, status_int):
        """sets all the valves"""
        current_status = self._valve_decode(status_int)
        self._update_status(current_status)

    def stop(self):
        """Switches off all the valves"""
        current_status = np.copy(self.status)
        current_status[:] = False
        print(" Switching OFF all valves")
        self._update_status(current_status)

    def shutdown(self):
        """Shutdowns the system"""
        print(" Shutting down")
        self.command_subscriber.running = False


def main():
    """Create and start a valve_controller Device object."""

    arguments = docopt(__doc__)

    device = ValveController(commands=parse_host_and_port(arguments["--commands"]),
                             status=parse_host_and_port(arguments["--status"]))

    device.command_subscriber.run_blocking()


if __name__ == "__main__":
    main()
