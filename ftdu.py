# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# License: BSD License
#
"""\
Python client to communicate with an ftDuino via USB.

It uses the ```ftduino_direct``` sketch written by Peter Habermehl.
See <https://github.com/PeterDHabermehl/ftduino_direct>
"""
from __future__ import absolute_import, unicode_literals, print_function
import time
import serial
import serial.tools.list_ports

__version__ = '0.0.1'

# <https://wiki.python.org/moin/PortingToPy3k/BilingualQuickRef#New_Style_Classes>
__metaclass__ = type


INPUT_MODE_SWITCH = 'switch'
INPUT_MODE_RESISTANCE = 'resistance'
INPUT_MODE_VOLTAGE = 'voltage'

_VALID_INPUT_MODES = (INPUT_MODE_SWITCH, INPUT_MODE_RESISTANCE, INPUT_MODE_VOLTAGE)

MOTOR_LEFT = 'left'
MOTOR_RIGHT = 'right'
MOTOR_BRAKE = 'brake'

_VALID_MOTOR_DIRECTIONS = (MOTOR_LEFT, MOTOR_RIGHT, MOTOR_BRAKE)

COUNTER_EDGE_NONE = 'none'
COUNTER_EDGE_RISING = 'rising'
COUNTER_EDGE_FALLING = 'falling'
COUNTER_EDGE_ANY = 'any'

_VALID_COUNTER_MODES = (COUNTER_EDGE_NONE, COUNTER_EDGE_RISING,
                        COUNTER_EDGE_FALLING, COUNTER_EDGE_ANY)

OFF = 0
HIGH = 1
LOW = 2

_MIN_PWM = 0
_MAX_PWM = 512


class FtDuino:
    """\
    This class provides an easy access to the ftDuino.

    An instance communicates via USB with a ftDuino. While providing several
    high level functions, it provides also access to the low level commands
    using :py:func:`comm`.

    The input and output ports are provided as attributes. Please note that
    they use lowercase names.

    The red LED can be switched on and off via ```led = True``` or ```led = False```.
    """
    def __init__(self, path=None):
        """\
        Iniatializes the connection to a ftDuino.

        If the `path` is ```None`` (default), the first ftDuino found by a scan
        will be used.

        :param path: Optoinal device path to ftDuino.
        """
        if path is None:
            try:
                path, name = next(ftduino_iter())
            except StopIteration:
                pass  # Handled in next line
        if path is None:
            raise ValueError('No ftDuino found.')
        self._conn = serial.Serial(path, 115200, timeout=0.1, writeTimeout=0.1)
        time.sleep(0.25)

    def comm(self, cmd):
        """\
        Low level access to the ftDuino.

        See <https://github.com/PeterDHabermehl/ftduino_direct#use> for a list
        of commands.

        :param cmd: The command to execute.
        :rtype: str
        :return: The result of the command.
        """
        conn = self._conn
        conn.reset_input_buffer()
        conn.reset_output_buffer()
        cmd += '\n'
        conn.write(cmd.encode('utf-8'))
        data = conn.readline().decode('utf-8')
        if data == '\n':
            return None
        return data[:-2]

    def close(self):
        """\
        Closes the connection to the ftDuino.
        """
        self._conn.close()

    def output_set(self, port, mode, pwm=None):
        """\
        Sets the provided output port into the provided mode.

        See also the attributes ```o1 .. o8``` for an easier access.

        :param port: Port name, i.e. 'O1'. The port name is case-insensitive.
        :param mode: 0 = OFF, 1 = HIGH, 2 = LOW
        :param pwm: Pulse-width modulation value. If ```None``` the value
                    depends on the mode. If the mode is ```1``` (high), the
                    pwm will be set to the max. pwm value, otherwise to the
                    min. pwm value.
        """
        if mode not in (0, HIGH, LOW):
            raise ValueError('Invalid mode "{0}". Use 0, 1 or 2.'.format(mode))
        if pwm is None:
            pwm = _MAX_PWM if mode == HIGH else _MIN_PWM
        self.comm('output_set {0} {1} {2}'.format(port, mode, pwm))

    def _set_output(self, port, value):
        """\
        Internal method which checks if value is a boolean. Otherwise, a tuple
        is expected.
        """
        pwm = None
        if value is True:
            mode = HIGH
        elif value is False:
            mode = LOW
        else:
            mode, pwm = value
        self.output_set(port, mode, pwm)

    def input_get(self, port):
        """\
        Reads a value from the provided input port.

        See also the attributes ```i1 .. i8``` for an easier access.

        :param port: Port name, i.e. 'I1'. The port name is case-insensitive.
        :rtype: int
        :return: The integer value read from the specified port.
        :raise: ValueError in case of an error.
        """
        return int(self.comm('input_get {0}'.format(port)))

    def input_set_mode(self, port, mode):
        """\
        Sets the mode for the provided input port.

        See also the attributes ```i1_mode .. i8_mode``` for an easier access.

        :param port: Port name, i.e. 'I1'. The port name is case-insensitive.
        :param mode: 'switch', 'resistance', or 'voltage' (case-insensitive)
        :raise: ValueError in case the provided mode is unknown.
        """
        if mode.lower() not in _VALID_INPUT_MODES:
            raise ValueError('Invalid mode "{0}". Use one of: {1}'.format(mode, _VALID_INPUT_MODES))
        self.comm('input_set_mode {0} {1}'.format(port, mode))

    def _set_led(self, enable):
        """\
        Sets the LED on / off.

        :param bool enable: ```True``` to put the light on, ```False``` to switch it off.
        """
        self.comm('led_set {0}'.format(1 if enable else 0))

    def counter_set_mode(self, port, mode):
        """\
        Sets the mode of the provided counter.

        :param port: Port name, i.e. 'C1'. The port name is case-insensitive.
        :param mode: 'none', 'rising', 'falling', or 'any' (case-insensitive)
        :return:
        """
        if mode.lower() not in _VALID_COUNTER_MODES:
            raise ValueError('Invalid mode "{0}". Use {1}'.format(mode, _VALID_COUNTER_MODES))
        self.comm('counter_set_mode {0} {1}'.format(port, mode))

    def counter_get(self, port):
        """\
        Returns the value of the provided counter port.

        See also the attributes ```c1 .. c4``` for an easier access.

        :param port: Port name, i.e. 'C1'. The port name is case-insensitive.
        :rtype: int
        :return: The value of the provided counter.
        """
        return int(self.comm('counter_get {0}'.format(port)))

    def counter_clear(self, port):
        """\
        Clears the provided counter port.

        Shortcut: Use the ```c1 .. c4``` attributes. I.e.  ```ftd.c1 = None```

        :param port: Port name, i.e. 'C1'. The port name is case-insensitive.
        """
        self.comm('counter_clear {0}'.format(port))

    def _counter_clear(self, port, val):
        """\
        Internal method which checks if val is either 0 or None, which is used
        to inidcate counter clearing.
        """
        if val not in (0, None):
            raise ValueError('Only 0 and None are valid values')
        self.counter_clear(port)

    def counter_get_state(self, port):
        """\
        Returns the state of the provied counter port.

        :param port: Port name, i.e. 'C1'. The port name is case-insensitive.
        :rtype: bool
        :return: The state, a boolean of the port.
        """
        return self.comm('counter_get_state {0}'.format(port)) == '1'

    def ultrasonic_get(self):
        """\
        Reads and returns the value of the ultrasonic sensor.

        Use the attribute "ultrasonic" as shortcut.

        :rtype: int
        :return: The value of the ultrasonic sensor.
        """
        return int(self.comm('ultrasonic_get'))

    def ultrasonic_enable(self, enable):
        """\
        Enables / disables the ultrasonic sensor.

        :param bool enable: ```True``` to enable, ```False``` to disable.
        """
        self.comm('ultrasonic_enable {0}'.format('true' if enable else 'false'))

    def motor_set(self, port, mode, pwm=None):
        """\
        Sets the provided motor port into the given state.

        :param port: Port name, i.e. 'M1'. The port name is case-insensitive.
        :param mode: 'left', 'right', or 'brake' (case-insensitive).
        :param pwm: Pulse-width modulation value. If ```None``` the max. PWM value will be used.
        """
        if mode.lower() not in _VALID_MOTOR_DIRECTIONS:
            raise ValueError('Invalid direction "{0}", use {1}'.format(mode, _VALID_MOTOR_DIRECTIONS))
        if pwm is None:
            pwm = _MAX_PWM
        self.comm('motor_set {0} {1} {2}'.format(port, mode, pwm))

    def motor_counter(self, port, mode, pwm, counter):
        """\
        Sets the motor counter into the given state.

        :param port: Port name, i.e. 'M1'. The port name is case-insensitive.
        :param mode: 'left', 'right', or 'brake' (case-insensitive).
        :param pwm: Pulse-width modulation value.
        :param counter: Counter value. The motor stops after reaching the value.
        """
        if mode.lower() not in _VALID_MOTOR_DIRECTIONS:
            raise ValueError('Invalid direction "{0}", use {1}'.format(mode, _VALID_MOTOR_DIRECTIONS))
        self.comm('motor_counter {0} {1} {2} {3}'.format(port, mode, pwm, counter))

    def motor_counter_active(self, port):
        """\
        Returns if a counter is active for the given motor port.

        :param port: Port name, i.e. 'M1'. The port name is case-insensitive.
        :return: ```True``` if the counter is active, otherwise ```False``.
        """
        return self.comm('motor_counter_active {0}'.format(port)) == '1'

    def motor_counter_set_brake(self, port, enable):
        """\
        Indicates if the motor should be stopped indirect (```False``) or direct
        (```True```).

        :param port: Port name, i.e. 'M1'. The port name is case-insensitive.
        :param enable: ```True``` to set the brake, otherwise ```False```
        """
        self.comm('motor_counter_set_brake {0} {1}'.format(port, ('true' if enable else 'false')))

    led = property(None, _set_led)

    o1 = property(None, lambda self, val: self._set_output('O1', val))
    o2 = property(None, lambda self, val: self._set_output('O2', val))
    o3 = property(None, lambda self, val: self._set_output('O3', val))
    o4 = property(None, lambda self, val: self._set_output('O4', val))
    o5 = property(None, lambda self, val: self._set_output('O5', val))
    o6 = property(None, lambda self, val: self._set_output('O6', val))
    o7 = property(None, lambda self, val: self._set_output('O7', val))
    o8 = property(None, lambda self, val: self._set_output('O8', val))

    i1 = property(lambda self: self.input_get('I1'))
    i2 = property(lambda self: self.input_get('I2'))
    i3 = property(lambda self: self.input_get('I3'))
    i4 = property(lambda self: self.input_get('I4'))
    i5 = property(lambda self: self.input_get('I5'))
    i6 = property(lambda self: self.input_get('I6'))
    i7 = property(lambda self: self.input_get('I7'))
    i8 = property(lambda self: self.input_get('I8'))
    i1_mode = property(None, lambda self, val: self.input_set_mode('I1', val))
    i2_mode = property(None, lambda self, val: self.input_set_mode('I2', val))
    i3_mode = property(None, lambda self, val: self.input_set_mode('I3', val))
    i4_mode = property(None, lambda self, val: self.input_set_mode('I4', val))
    i5_mode = property(None, lambda self, val: self.input_set_mode('I5', val))
    i6_mode = property(None, lambda self, val: self.input_set_mode('I6', val))
    i7_mode = property(None, lambda self, val: self.input_set_mode('I7', val))
    i8_mode = property(None, lambda self, val: self.input_set_mode('I8', val))

    c1 = property(lambda self: self.counter_get('C1'), lambda self, val: self._counter_clear('C1', val))
    c2 = property(lambda self: self.counter_get('C2'), lambda self, val: self._counter_clear('C2', val))
    c3 = property(lambda self: self.counter_get('C3'), lambda self, val: self._counter_clear('C3', val))
    c4 = property(lambda self: self.counter_get('C4'), lambda self, val: self._counter_clear('C4', val))
    c1_mode = property(None, lambda self, val: self.counter_set_mode('C1', val))
    c2_mode = property(None, lambda self, val: self.counter_set_mode('C2', val))
    c3_mode = property(None, lambda self, val: self.counter_set_mode('C3', val))
    c4_mode = property(None, lambda self, val: self.counter_set_mode('C4', val))
    c1_state = property(lambda self: self.counter_get_state('C1'))
    c2_state = property(lambda self: self.counter_get_state('C2'))
    c3_state = property(lambda self: self.counter_get_state('C3'))
    c4_state = property(lambda self: self.counter_get_state('C4'))

    ultrasonic = property(ultrasonic_get)


def ftduino_iter():
    """\
    Returns an iterator / generator over all ftDuinos connected to the host device.
    """
    # FTDUINO_VIRGIN_VIDPID = '1c40:0537', FTDUINO_VIDPID = '1c40:0538'
    for lpi in serial.tools.list_ports.grep(r'vid:pid=1c40:053[78]'):
        path = lpi.device
        with serial.Serial(path, 115200, timeout=0.1, writeTimeout=0.1) as conn:
            time.sleep(0.25)
            conn.reset_input_buffer()
            conn.reset_output_buffer()
            conn.write('ftduino_id_get\n'.encode('utf-8'))
            name = conn.readline().decode('utf-8')[:-2]
        yield path, name


def ftduino_find_by_name(name):
    """
    Returns the path of the ftDuino with the specified `name`.

    :param name: Name of the ftDuino.
    :return: The path of the ftDuino or ```None``` if the ftDuino was not found.
    """
    for path, device_name in ftduino_iter():
        if name == device_name:
            return path
    return None
