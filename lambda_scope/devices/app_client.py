#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand, Vivek Venkatachalam

import signal

import zmq
from docopt import docopt

from lambda_scope.zmq.utils import (
    coerce_string,
    coerce_bytes
)

class Client():
    """This is a wrapped ZMQ client that can send requests to a server."""

    def __init__(
            self,
            port):

        self.port = port
        self.running = False

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.REQ)

        address = "tcp://localhost:{}".format(self.port)
        self.socket.connect(address)

        self.reply = ''

    def recv(self) -> bytes:
        """Receive a reply."""

        return self.socket.recv()

    def send(self, req: bytes):
        """Send a request."""

        self.socket.send(req)

    def process(self, req_str):
        """Take a single request from stdin, send
        it to a server, and return the reply."""

        self.send(coerce_bytes(req_str))
        self.reply = coerce_string(self.recv())
