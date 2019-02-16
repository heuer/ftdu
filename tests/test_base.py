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


if __name__ == '__main__':
    pytest.main([ __file__])
