#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand, Vivek Venkatachalam

"""This contains tools to send arrays of numbers between processes using TCP
and ZeroMQ's Pub/Sub."""

from typing import Tuple, Optional

import zmq
import numpy as np

from lambda_scope.zmq.utils import (
    get_last,
    push_timestamp,
    pop_timestamp)

class Publisher():
    """This publishes arrays over TCP using ZMQ."""

    def __init__(
            self,
            host: str,
            port: int,
            shape: Tuple[int, ...],
            datatype: np.dtype,
            bound=False):

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        self.bound = bound
        address = "tcp://{}:{}".format(host, port)
        if bound:
            self.socket.bind(address)
        else:
            self.socket.connect(address)

        self.shape = shape
        self.dtype = np.dtype(datatype)
        self.numel = np.prod(shape)
        self.nbytes = self.numel * self.dtype.itemsize

    def send(self, data):
        """Publish an array."""
        self.socket.send(data)

class TimestampedPublisher(Publisher):
    """This publishes arrays after appending timestamps as float64s."""

    def send(self, data):
        """Publish a time stamped array."""
        data = push_timestamp(bytes(data))
        self.socket.send(data)

class Subscriber():
    """This is a ZMQ subscriber that interprets messages as arrays."""

    def __init__(
            self,
            host: str,
            port: int,
            shape: Tuple[int, ...],
            datatype: np.dtype,
            bound=False):

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)

        self.bound = bound
        self.address = "tcp://{}:{}".format(host, port)
        if self.bound:
            self.socket.bind(self.address)
        else:
            self.socket.connect(self.address)

        self.socket.setsockopt(zmq.SUBSCRIBE, b"")

        self.shape = shape
        self.dtype = np.dtype(datatype)

        self.numel = np.prod(shape)
        self.nbytes = self.numel * self.dtype.itemsize

    def recv(self) -> np.ndarray:
        """ This will block until a message appears on the channel, and if
        multiple messages are present it will return them in order."""
        buf = self.socket.recv()
        return self.array_from_bytes(buf)

    def get_last(self) -> Optional[np.ndarray]:
        """ This will return the most recent message present on the channel,
        and if no messages are present it will return None."""
        buf = get_last(self.socket.recv)

        if buf is None:
            return None

        return self.array_from_bytes(buf)

    def array_from_bytes(self, buf: bytes) -> np.ndarray:
        """Convert a message of bytes into an array."""

        array_buf = buf[:self.nbytes]
        data = np.frombuffer(array_buf, self.dtype)
        shape = self.shape
        shape_list = list(shape)
        return data.reshape(shape_list)

class TimestampedSubscriber(Subscriber):
    """This subscribes to arrays generated by a TimestampedPublisher."""

    def recv(self) -> Tuple[float, np.ndarray]:
        buf = self.socket.recv()
        return self.unpack_buffer(buf)

    def get_last(self) -> Optional[Tuple[float, np.ndarray]]:
        buf = get_last(self.socket.recv)

        if buf is None:
            return None

        return self.unpack_buffer(buf)

    def unpack_buffer(self, buf: bytes) -> Tuple[float, np.ndarray]:
        """Convert a buffer containing an image and a timestamp into a tuple
        with both."""

        (timestamp, buf) = pop_timestamp(buf)
        data = self.array_from_bytes(buf)
        return (timestamp, data)
