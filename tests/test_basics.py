# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# License: BSD License
#
from __future__ import unicode_literals, absolute_import
import pytest
import ftdu


def test_ultrasonic():
    ftd = ftdu.FtDuino()
    assert ftd.ultrasonic == -1


def test_ultrasonic_enable():
    ftd = ftdu.FtDuino()
    ftd.ultrasonic_enable(True)
    ftd.ultrasonic_enable(False)


if __name__ == '__main__':
    pytest.main([ __file__])
