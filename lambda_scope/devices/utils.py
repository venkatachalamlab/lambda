#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand, Vivek Venkatachalam

"""This module contains utilities used in devices."""

import os
import datetime
from typing import Tuple

import numpy as np

def make_timestamped_filename(directory: str, stub: str, ext: str):
    """Create a file name containing date and time."""

    now = datetime.datetime.now()
    filename = "%s_%04d_%02d_%02d_%02d_%02d_%02d.%s" % (
        stub, now.year, now.month, now.day, now.hour, now.minute, now.second,
        ext)
    return os.path.join(directory, filename)


def array_props_from_string(fmt: str) -> Tuple[np.dtype, str, Tuple[int, ...]]:
    """Convert a string describing the datatype, layout, and shape of an array
    into a tuple containing that information."""

    (dtype, layout, *shape) = fmt.split("_")
    dtype = np.dtype(dtype.lower())
    shape = tuple(map(int, shape))

    return (dtype, layout, shape)
