# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# License: BSD License
#
"""\
Tests against BaseFtDuino.
"""
from __future__ import unicode_literals, absolute_import
import pytest
import ftdu


def test_ultrasonic_enable():
    with ftdu.BaseFtDuino() as ftd:
        ftd.ultrasonic_enable(True)
        ftd.ultrasonic_enable(False)


def test_outputset_illegal():
    with ftdu.BaseFtDuino() as ftd:
        with pytest.raises(ValueError) as ex:
            ftd.output_set('O2', 28, ftdu.MAX)


def test_motor_set():
    with ftdu.BaseFtDuino() as ftd:
        ftd.motor_set('M1', ftdu.MOTOR_RIGHT)
        ftd.motor_set('M2', ftdu.MOTOR_LEFT)
        ftd.motor_set('M3', ftdu.MOTOR_OFF)
        ftd.motor_set('M4', ftdu.MOTOR_BRAKE)


def test_motor_set_illegal():
    with ftdu.BaseFtDuino() as ftd:
        with pytest.raises(ValueError) as ex:
            ftd.motor_set('M1', 'forward')


def test_ftduino_id():
    with ftdu.BaseFtDuino() as ftd:
        id_prev = ftd.ftduino_id_get()
        assert id_prev
        id_new = 'Pitje Puck'
        ftd.ftduino_id_set(id_new)
        assert id_new == ftd.ftduino_id_get()
        # Reset ID
        ftd.ftduino_id_set(id_prev)
        assert id_prev == ftd.ftduino_id_get()


def test_ftduino_version():
    with ftdu.BaseFtDuino() as ftd:
        assert ftd.ftduino_direct_get_version()


def test_find_by_name():
    names = [name for x, name in ftdu.ftduino_iter() if name is not None]
    if not names:
        return
    name = names[0]
    assert name
    path = ftdu.ftduino_find_by_name(name)
    assert path
    invalid_name = name
    while invalid_name in names:
        invalid_name += 'x'
    path = ftdu.ftduino_find_by_name(invalid_name)
    assert path is None


if __name__ == '__main__':
    pytest.main([ __file__])
