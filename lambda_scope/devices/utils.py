#! python
#
# Copyright 2021
# Author: Mahdi Torkashvand, Vivek Venkatachalam

"""This module contains utilities used in devices."""

import os
import datetime

def make_timestamped_filename(directory: str, stub: str, ext: str):
    """Create a file name containing date and time."""

    now = datetime.datetime.now()
    filename = "%s_%04d_%02d_%02d_%02d_%02d_%02d.%s" % (
        stub, now.year, now.month, now.day, now.hour, now.minute, now.second,
        ext)
    return os.path.join(directory, filename)