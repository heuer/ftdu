# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# License: BSD License
#
"""\
ftDuino Handbuch - 4.8.1 Einfache Ampel.
"""
import time
import ftdu


def example():
    with ftdu.FtDuino() as ftd:
        setup(ftd)
        while True:
            loop(ftd)


def setup(ftd):
    ftd.o1 = True


def loop(ftd):
    if ftd.i1:
        ftd.o1 = False  # Rote Lampe ausschalten
        ftd.o2 = True  # Grüne Lampe einschalten
        time.sleep(10)  # 10 Sek. warten
        ftd.o1 = True
        ftd.o2 = False


if __name__ == '__main__':
    example()
