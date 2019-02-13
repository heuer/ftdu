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


def test_input_props():
    ftd = ftdu.FtDuino()
    assert ftd.i1 == 0
    assert ftd.i2 == 0
    assert ftd.i3 == 0
    assert ftd.i4 == 0
    assert ftd.i5 == 0
    assert ftd.i6 == 0
    assert ftd.i7 == 0
    assert ftd.i8 == 0


def test_input_mode():
    ftd = ftdu.FtDuino()
    ftd.i1_mode = ftdu.INPUT_MODE_RESISTANCE
    ftd.i1_mode = ftdu.INPUT_MODE_VOLTAGE
    ftd.i1_mode = ftdu.INPUT_MODE_SWITCH


def test_input_mode_error():
    ftd = ftdu.FtDuino()
    with pytest.raises(ValueError) as ex:
        ftd.i1_mode = 'illegal'



if __name__ == '__main__':
    pytest.main([ __file__])
