# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# License: BSD License
#
"""\
ftDuino Handbuch - 3.1 Der erste Sketch
"""
import time
import ftdu


def example():
    with ftdu.FtDuino() as ftd:
        setup(ftd)
        while True:
            loop(ftd)


def setup(ftd):
    pass


def loop(ftd):
    ftd.led = True
    ftd.o1 = True
    time.sleep(1)
    ftd.led = False
    ftd.o1 = False
    time.sleep(1)


if __name__ == '__main__':
    example()
