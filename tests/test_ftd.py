# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# License: BSD License
#
"""\
Tests against FtDuino
"""
from __future__ import unicode_literals, absolute_import
import pytest
import ftdu


def test_input_props():
    with ftdu.FtDuino() as ftd:
        assert ftd.i1 == 0
        assert ftd.i2 == 0
        assert ftd.i3 == 0
        assert ftd.i4 == 0
        assert ftd.i5 == 0
        assert ftd.i6 == 0
        assert ftd.i7 == 0
        assert ftd.i8 == 0


def test_input_mode():
    with ftdu.FtDuino() as ftd:
        ftd.i1_mode = ftdu.INPUT_MODE_RESISTANCE
        ftd.i1_mode = ftdu.INPUT_MODE_VOLTAGE
        ftd.i1_mode = ftdu.INPUT_MODE_SWITCH


def test_input_mode_error():
    with ftdu.FtDuino() as ftd:
        with pytest.raises(ValueError) as ex:
            ftd.i1_mode = 'illegal'


def test_output_props():
    with ftdu.FtDuino() as ftd:
        ftd.o1 = True
        ftd.o2 = False
        ftd.o3 = ftdu.OFF
        ftd.o4 = ftdu.HIGH
        ftd.o5 = ftdu.LOW
        ftd.o6 = ftdu.HIGH, ftdu.MAX / 2
        ftd.o7 = True
        ftd.o8 = False


def test_output_props_illegal():
    with ftdu.FtDuino() as ftd:
        with pytest.raises(TypeError) as ex:
            ftd.o1 = 42


def test_output_props_illegal2():
    with ftdu.FtDuino() as ftd:
        with pytest.raises(ValueError) as ex:
            ftd.o1 = 'true'


def test_counter_props():
    with ftdu.FtDuino() as ftd:
        ftd.c1_clear()
        ftd.c2_clear()
        ftd.c3_clear()
        ftd.c4_clear()
        assert ftd.c1 == 0
        assert ftd.c2 == 0
        assert ftd.c3 == 0
        assert ftd.c4 == 0


def test_counter_clear():
    with ftdu.FtDuino() as ftd:
        ftd.c1_clear()
        ftd.c2_clear()
        ftd.c3_clear()
        ftd.c4_clear()


def test_counter_states():
    with ftdu.FtDuino() as ftd:
        assert not ftd.c1_state
        assert not ftd.c2_state
        assert not ftd.c3_state
        assert not ftd.c4_state


def test_counter_mode():
    with ftdu.FtDuino() as ftd:
        ftd.c1_mode = ftdu.COUNTER_EDGE_NONE
        ftd.c2_mode = ftdu.COUNTER_EDGE_RISING
        ftd.c3_mode = ftdu.COUNTER_EDGE_FALLING
        ftd.c4_mode = ftdu.COUNTER_EDGE_ANY


def test_counter_mode_illegal():
    with ftdu.FtDuino() as ftd:
        with pytest.raises(ValueError) as ex:
            ftd.c1_mode = 'illegal'


def test_ultrasonic():
    with ftdu.FtDuino() as ftd:
        assert -1 == ftd.ultrasonic


def test_led():
    with ftdu.FtDuino() as ftd:
        ftd.led = True
        ftd.led = False


def test_motor_counter_state():
    with ftdu.FtDuino() as ftd:
        #TODO: The tests motor_left and motor_right may change the state of the counters.
        # Usually we should be able to test: assert not ftd.m1_counter_active
        assert ftd.m1_counter_active in (True, False)
        assert ftd.m2_counter_active in (True, False)
        assert ftd.m3_counter_active in (True, False)
        assert ftd.m4_counter_active in (True, False)


def test_motor_left():
    with ftdu.FtDuino() as ftd:
        ftd.m1_left()
        ftd.m2_left(steps=23)
        ftd.m3_left(pwm=ftdu.MAX)
        ftd.m4_left(pwm=ftdu.MAX / 2, steps=47)


def test_motor_right():
    with ftdu.FtDuino() as ftd:
        ftd.m1_right()
        ftd.m2_right(steps=23)
        ftd.m3_right(pwm=ftdu.MAX)
        ftd.m4_right(pwm=ftdu.MAX / 2, steps=47)


if __name__ == '__main__':
    pytest.main([ __file__])
