# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# License: BSD License
#
"""\
Python client to communicate with a ftDuino via USB.

It uses the ``ftduino_direct`` sketch written by Peter Habermehl.
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

MOTOR_OFF = 'off'
MOTOR_LEFT = 'left'
MOTOR_RIGHT = 'right'
MOTOR_BRAKE = 'brake'

_VALID_MOTOR_DIRECTIONS = (MOTOR_LEFT, MOTOR_RIGHT, MOTOR_BRAKE, MOTOR_OFF)

COUNTER_EDGE_NONE = 'none'
COUNTER_EDGE_RISING = 'rising'
COUNTER_EDGE_FALLING = 'falling'
COUNTER_EDGE_ANY = 'any'

_VALID_COUNTER_MODES = (COUNTER_EDGE_NONE, COUNTER_EDGE_RISING,
                        COUNTER_EDGE_FALLING, COUNTER_EDGE_ANY)

OFF = 0
HIGH = 1
LOW = 2

MIN = OFF
# Should be 62, see <https://github.com/PeterDHabermehl/ftduino_direct/issues/4>
MAX = 512


class BaseFtDuino:
    """\
    Base class to communicate with a ftDuino.

    This class implements all high level functions of the ftDuino API.

    To issue other commands, the :py:func:`comm` method can be used.
    """
    def __init__(self, path=None):
        """\
        Initializes a connection to a ftDuino.

        If the `path` is ``None`` (default), the first ftDuino found by a scan
        will be used.

        :param path: Optional device path to ftDuino.
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def comm(self, cmd):
        """\
        Low level access to the ftDuino.

        See <https://github.com/PeterDHabermehl/ftduino_direct#use> for a list
        of commands.

        :param cmd: The command to execute.
        :rtype: str
        :return: The result of the command or ``None`` in case of an error.
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

        Use the ``with`` statement to ensure that this method is called.

        .. code-block:: python

            with BaseFtduino() as ftd:
                ftd.led = True
        """
        self._conn.close()

    def output_set(self, port, mode, pwm=None):
        """\
        Sets the provided output port into the provided mode.

        :param port: Port name, i.e. 'O1'. The port name is case-insensitive.
        :param mode: 0 = OFF, 1 = HIGH, 2 = LOW
        :param pwm: Pulse-width modulation value. If ``None`` the value
                    depends on the mode. If the mode is ``1`` (high), the
                    pwm will be set to the max. pwm value, otherwise to the
                    min. pwm value.
        """
        if mode not in (OFF, HIGH, LOW):
            raise ValueError('Invalid mode "{0}". Use 0, 1 or 2.'.format(mode))
        if pwm is None:
            pwm = MAX if mode == HIGH else MIN
        self.comm('output_set {0} {1} {2}'.format(port, mode, pwm))

    def input_get(self, port):
        """\
        Reads a value from the provided input port.

        :param port: Port name, i.e. 'I1'. The port name is case-insensitive.
        :rtype: int
        :return: The integer value read from the specified port.
        :raise: ValueError in case of an error.
        """
        return int(self.comm('input_get {0}'.format(port)))

    def input_set_mode(self, port, mode):
        """\
        Sets the mode for the provided input port.

        :param port: Port name, i.e. 'I1'. The port name is case-insensitive.
        :param mode: 'switch', 'resistance', or 'voltage' (case-insensitive), see
                     constants ``ftdu.INPUT_MODE_SWITCH``, ``ftdu.INPUT_MODE_RESISTANCE``
                     and ``ftdu.INPUT_MODE_VOLTAGE``.
        :raise: ValueError in case the provided mode is unknown.
        """
        if mode.lower() not in _VALID_INPUT_MODES:
            raise ValueError('Invalid mode "{0}". Use one of: {1}'.format(mode, _VALID_INPUT_MODES))
        self.comm('input_set_mode {0} {1}'.format(port, mode))

    def counter_set_mode(self, port, mode):
        """\
        Sets the mode of the provided counter.

        :param port: Port name, i.e. 'C1'. The port name is case-insensitive.
        :param mode: 'none', 'rising', 'falling', or 'any' (case-insensitive)
        """
        if mode.lower() not in _VALID_COUNTER_MODES:
            raise ValueError('Invalid mode "{0}". Use {1}'.format(mode, _VALID_COUNTER_MODES))
        self.comm('counter_set_mode {0} {1}'.format(port, mode))

    def counter_get(self, port):
        """\
        Returns the value of the provided counter port.

        :param port: Port name, i.e. 'C1'. The port name is case-insensitive.
        :rtype: int
        :return: The value of the provided counter.
        """
        return int(self.comm('counter_get {0}'.format(port)))

    def counter_clear(self, port):
        """\
        Clears the provided counter port.

        :param port: Port name, i.e. 'C1'. The port name is case-insensitive.
        """
        self.comm('counter_clear {0}'.format(port))

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

        :rtype: int
        :return: The value of the ultrasonic sensor.
        """
        return int(self.comm('ultrasonic_get'))

    def ultrasonic_enable(self, enable):
        """\
        Enables / disables the ultrasonic sensor.

        :param bool enable: ``True`` to enable, ``False`` to disable.
        """
        self.comm('ultrasonic_enable {0}'.format('true' if enable else 'false'))

    def motor_set(self, port, mode, pwm=None):
        """\
        Sets the provided motor port into the given state.

        :param port: Port name, i.e. 'M1'. The port name is case-insensitive.
        :param mode: 'off',  'left', 'right', or 'brake' (case-insensitive), see constants
                     ``ftdu.MOTOR_OFF``, ``ftdu.MOTOR_LEFT``, ``ftdu.MOTOR_RIGHT``,
                     and ``ftdu.MOTOR_BRAKE``.
        :param pwm: Pulse-width modulation value. If ``None`` the max. PWM value will be used.
        """
        if mode.lower() not in _VALID_MOTOR_DIRECTIONS:
            raise ValueError('Invalid motor mode "{0}", use {1}'.format(mode, _VALID_MOTOR_DIRECTIONS))
        if pwm is None:
            pwm = MAX
        self.comm('motor_set {0} {1} {2}'.format(port, mode, pwm))

    def motor_counter(self, port, mode, pwm, counter):
        """\
        Sets the state of an encoder motor.

        :param port: Port name, i.e. 'M1'. The port name is case-insensitive.
        :param mode: 'off',  'left', 'right', or 'brake' (case-insensitive), see constants
                     ``ftdu.MOTOR_OFF``, ``ftdu.MOTOR_LEFT``, ``ftdu.MOTOR_RIGHT``,
                     and ``ftdu.MOTOR_BRAKE``.
        :param pwm: Pulse-width modulation value.
        :param counter: Counter value. The motor stops after reaching the value.
        """
        if mode.lower() not in _VALID_MOTOR_DIRECTIONS:
            raise ValueError('Invalid motor mode "{0}", use {1}'.format(mode, _VALID_MOTOR_DIRECTIONS))
        self.comm('motor_counter {0} {1} {2} {3}'.format(port, mode, pwm, counter))

    def motor_counter_active(self, port):
        """\
        Returns if a counter is active for the given motor port.

        :param port: Port name, i.e. 'M1'. The port name is case-insensitive.
        :return: ``True`` if the counter is active, otherwise ``False``.
        """
        return self.comm('motor_counter_active {0}'.format(port)) == '1'

    def motor_counter_set_brake(self, port, enable):
        """\
        Indicates if the motor should be stopped indirectly (``False``) or
        directly (``True``).

        :param port: Port name, i.e. 'M1'. The port name is case-insensitive.
        :param enable: ``True`` to set the brake, otherwise ``False``
        """
        self.comm('motor_counter_set_brake {0} {1}'.format(port, ('true' if enable else 'false')))

    def led_set(self, enable):
        """\
        Switches the LED on or off

        :param enable: ``True`` to switch the LED on, ``False`` to switch the LED off.
        """
        self.comm('led_set {0}'.format(1 if enable else 0))

    #
    # ftduino_direct commands
    #
    def ftduino_direct_get_version(self):
        """\
        Returns the ftduino_direct version

        :return: A version string.
        """
        return self.comm('ftduino_direct_get_version')

    def ftduino_id_get(self):
        """\
        Returns the ID of the connected ftDuino.

        :return: The ID of the ftDuino.
        """
        return self.comm('ftduino_id_get')

    def ftduino_id_set(self, identifier):
        """\
        Sets the ftDuino ID.

        :param str|unicode identifier: The identifier.
        """
        self.comm('ftduino_id_set {0}'.format(identifier))


class FtDuino(BaseFtDuino):
    """\
    This class provides all functions of the :class:`BaseFtDuino` and
    adds a higher level API to access ports via attributes.

    The red LED can be switched on and off via ``led = True`` or ``led = False``.

    .. code-block:: python

        ftd = FtDuino()
        ftd.led = True  # Switches the LED on.


    The input ports can be read by using the port names (i1 .. i8), i.e.
    ``ftd.i1`` to get the value of input port "I1".

    The output ports (o1 .. o8) can be enabled / disabled by assigning a boolean
    value.

    Example:

    .. code-block:: python

        ftd = FtDuino()
        ftd.o1 = True   # Sets the output O1 to HIGH with a max. PWM value
        ftd.o2 = False  # Sets the output O2 to LOW with a min. PWM value


    Further, it is possible to specify the PWM value if a tuple is used:

    .. code-block:: python

        ftd = FtDuino()
        ftd.o1 = ftdu.HIGH, ftdu.MAX / 2  # Sets the output O1 to HIGH with half speed


    This class provides also methods to control motors at the ports M1 .. M4.

    .. code-block:: python

        ftd = FtDuino()
        ftd.m1_left()   # Rotation left at full speed
        ftd.m1_right(pwm=ftdu.MAX / 2)  # Rotation right with half speed

        # Rotation right, full speed, stop after 38 steps (encoder motor)
        ftd.m2_right(steps=38)
    """
    def __init__(self, path=None):
        """\
        See :class:`BaseFtDuino`
        """
        super(FtDuino, self).__init__(path)

    @property
    def m1_counter_active(self):
        """\
        Returns if the motor counter for port M1 is active.

        :return: ``True`` if active, ``False`` otherwise.
        """
        return self.motor_counter_active('M1')

    def m1_left(self, pwm=None, steps=None):
        """\
        Sets the rotation of the motor at M1 to "left".

        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_left('M1', pwm, steps)

    def m1_right(self, pwm=None, steps=None):
        """\
        Sets the rotation of the motor at M1 to "right".

        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_right('M1', pwm, steps)

    def m1_off(self, steps=None):
        """\
        Switches the motor at M1 off.

        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_off('M1', steps)

    def m1_brake(self, pwm=None, steps=None):
        """\
        Brakes the motor at M1.

        See also :py:func:`motor_counter_set_brake`

        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_brake('M1', pwm, steps)

    @property
    def m2_counter_active(self):
        """\
        Returns if the motor counter for port M2 is active.

        :return: ``True`` if active, ``False`` otherwise.
        """
        return self.motor_counter_active('M2')

    def m2_left(self, pwm=None, steps=None):
        """\
        Sets the rotation of the motor at M2 to "left".

        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_left('M2', pwm, steps)

    def m2_right(self, pwm=None, steps=None):
        """\
        Sets the rotation of the motor at M2 to "right".

        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_right('M2', pwm, steps)

    def m2_off(self, steps=None):
        """\
        Switches the motor at M2 off.

        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_off('M2', steps)

    def m2_brake(self, pwm=None, steps=None):
        """\
        Brakes the motor at M2.

        See also :py:func:`motor_counter_set_brake`

        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_brake('M2', pwm, steps)

    @property
    def m3_counter_active(self):
        """\
        Returns if the motor counter for port M3 is active.

        :return: ``True`` if active, ``False`` otherwise.
        """
        return self.motor_counter_active('M3')

    def m3_left(self, pwm=None, steps=None):
        """\
        Sets the rotation of the motor at M3 to "left".

        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_left('M3', pwm, steps)

    def m3_right(self, pwm=None, steps=None):
        """\
        Sets the rotation of the motor at M3 to "right".

        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_right('M3', pwm, steps)

    def m3_off(self, steps=None):
        """\
        Switches the motor at M3 off.

        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_off('M3', steps)

    def m3_brake(self, pwm=None, steps=None):
        """\
        Brakes the motor at M3.

        See also :py:func:`motor_counter_set_brake`

        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_brake('M3', pwm, steps)

    @property
    def m4_counter_active(self):
        """\
        Returns if the motor counter for port M4 is active.

        :return: ``True`` if active, ``False`` otherwise.
        """
        return self.motor_counter_active('M4')

    def m4_left(self, pwm=None, steps=None):
        """\
        Sets the rotation of the motor at M4 to "left".

        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_left('M4', pwm, steps)

    def m4_right(self, pwm=None, steps=None):
        """\
        Sets the rotation of the motor at M4 to "right".

        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_right('M4', pwm, steps)

    def m4_off(self, steps=None):
        """\
        Switches the motor at M1 off.

        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_off('M4', steps)

    def m4_brake(self, pwm=None, steps=None):
        """\
        Brakes the motor at M4.

        See also :py:func:`motor_counter_set_brake`

        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        self._motor_brake('M4', pwm, steps)

    def _motor_left(self, port, pwm, steps):
        """\
        Sets the rotation of the motor at the provided port to "left".

        :param port: Motor port 'M1' .. 'M4'. The port name is case-insensitive.
        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        if pwm is None:
            pwm = MAX
        if steps is None:
            self.motor_set(port, MOTOR_LEFT, pwm)
        else:
            self.motor_counter(port, MOTOR_LEFT, pwm, steps)

    def _motor_right(self, port, pwm, steps):
        """\
        Sets the rotation of the motor at the provided port to "right".

        :param port: Motor port 'M1' .. 'M4'. The port name is case-insensitive.
        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        if pwm is None:
            pwm = MAX
        if steps is None:
            self.motor_set(port, MOTOR_RIGHT, pwm)
        else:
            self.motor_counter(port, MOTOR_RIGHT, pwm, steps)

    def _motor_off(self, port, steps):
        """\
        Switches the motor at the provided port off.

        :param port: Motor port 'M1' .. 'M4'. The port name is case-insensitive.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        pwm = OFF  # PWM is ignored for op MOTOR_OFF
        if steps is None:
            self.motor_set(port, MOTOR_OFF, pwm)
        else:
            self.motor_counter(port, MOTOR_OFF, pwm, steps)

    def _motor_brake(self, port, pwm, steps):
        """\
        Brakes the motor at the provided port.

        :param port: Motor port 'M1' .. 'M4'. The port name is case-insensitive.
        :param pwm: Pulse-width modulation value. If ``None`` the value is
                    set to the maximum.
        :param steps: Number of steps until the motor stops (encoder motor required).
        """
        if pwm is None:
            pwm = MAX
        if steps is None:
            self.motor_set(port, MOTOR_BRAKE, pwm)
        else:
            self.motor_counter(port, MOTOR_BRAKE, pwm, steps)

    def _set_motor_counter_brake(self, port, enable):
        """\
        Indicates if the motor should be stopped indirectly (``False``) or
        directly (``True``).

        :param port: Motor port 'M1' .. 'M4'. The port name is case-insensitive.
        :param enable: ``True`` to enable, ``False`` to disable.
        """
        self.motor_counter_set_brake(port, enable)

    def _set_output(self, port, value):
        """\
        Internal method to check if the output should be enabled / disabled
        via a single value (boolean, integer) or if the pwm was provided (a tuple
        was assigned)
        """
        pwm = None
        if value in (True, HIGH):
            mode = HIGH
        elif value is False:
            mode = OFF
        elif value in (OFF, LOW):
            mode = value
        else:
            mode, pwm = value
        self.output_set(port, mode, pwm)

    def _led_set(self, enable):
        """\
        Sets the LED on / off.

        :param bool enable: ``True`` to put the light on, ``False`` to switch it off.
        """
        self.led_set(enable)

    @property
    def ultrasonic(self):
        """\
        Returns the value of the ultrasonic sensor.

        :rtype: int
        :return: The value of the ultrasonic sensor.
        """
        return self.ultrasonic_get()

    @property
    def i1(self):
        """\
        Returns the value of input port "I1".

        :rtype: int
        :return: The value of input port "I1".
        """
        return self.input_get('I1')

    @property
    def i2(self):
        """\
        Returns the value of input port "I2".

        :rtype: int
        :return: The value of input port "I2".
        """
        return self.input_get('I2')

    @property
    def i3(self):
        """\
        Returns the value of input port "I3".

        :rtype: int
        :return: The value of input port "I3".
        """
        return self.input_get('I3')

    @property
    def i4(self):
        """\
        Returns the value of input port "I4".

        :rtype: int
        :return: The value of input port "I4".
        """
        return self.input_get('I4')

    @property
    def i5(self):
        """\
        Returns the value of input port "I5".

        :rtype: int
        :return: The value of input port "I5".
        """
        return self.input_get('I5')

    @property
    def i6(self):
        """\
        Returns the value of input port "I6".

        :rtype: int
        :return: The value of input port "I6".
        """
        return self.input_get('I6')

    @property
    def i7(self):
        """\
        Returns the value of input port "I7".

        :rtype: int
        :return: The value of input port "I7".
        """
        return self.input_get('I7')

    @property
    def i8(self):
        """\
        Returns the value of input port "I8".

        :rtype: int
        :return: The value of input port "I8".
        """
        return self.input_get('I8')

    @property
    def c1(self):
        """\
        Returns the value of counter "C1".

        :rtype: int
        :return: The value of counter "C1".
        """
        return self.counter_get('C1')

    def c1_clear(self):
        """\
        Clears counter C1 (sets the counter value to zero).
        """
        self.counter_clear('C1')

    @property
    def c2(self):
        """\
        Returns the value of counter "C2".

        :rtype: int
        :return: The value of counter "C2".
        """
        return self.counter_get('C2')

    def c2_clear(self):
        """\
        Clears counter C2 (sets the counter value to zero).
        """
        self.counter_clear('C2')

    @property
    def c3(self):
        """\
        Returns the value of counter "C3".

        :rtype: int
        :return: The value of counter "C3".
        """
        return self.counter_get('C3')

    def c3_clear(self):
        """\
        Clears counter C3 (sets the counter value to zero).
        """
        self.counter_clear('C3')

    @property
    def c4(self):
        """\
        Returns the value of counter "C4".

        :rtype: int
        :return: The value of counter "C4".
        """
        return self.counter_get('C4')

    def c4_clear(self):
        """\
        Clears counter C4 (sets the counter value to zero).
        """
        self.counter_clear('C4')

    @property
    def c1_state(self):
        """\
        Returns the state of counter "C1".

        :rtype: bool
        :return: ``True`` if the counter is active, otherwise ``False``.
        """
        return self.counter_get_state('C1')

    @property
    def c2_state(self):
        """\
        Returns the state of counter "C2".

        :rtype: bool
        :return: ``True`` if the counter is active, otherwise ``False``.
        """
        return self.counter_get_state('C2')

    @property
    def c3_state(self):
        """\
        Returns the state of counter "C3".

        :rtype: bool
        :return: ``True`` if the counter is active, otherwise ``False``.
        """
        return self.counter_get_state('C3')

    @property
    def c4_state(self):
        """\
        Returns the state of counter "C4".

        :rtype: bool
        :return: ``True`` if the counter is active, otherwise ``False``.
        """
        return self.counter_get_state('C4')

    led = property(None, _led_set)

    o1 = property(None, lambda self, val: self._set_output('O1', val))
    o2 = property(None, lambda self, val: self._set_output('O2', val))
    o3 = property(None, lambda self, val: self._set_output('O3', val))
    o4 = property(None, lambda self, val: self._set_output('O4', val))
    o5 = property(None, lambda self, val: self._set_output('O5', val))
    o6 = property(None, lambda self, val: self._set_output('O6', val))
    o7 = property(None, lambda self, val: self._set_output('O7', val))
    o8 = property(None, lambda self, val: self._set_output('O8', val))

    i1_mode = property(None, lambda self, val: self.input_set_mode('I1', val))
    i2_mode = property(None, lambda self, val: self.input_set_mode('I2', val))
    i3_mode = property(None, lambda self, val: self.input_set_mode('I3', val))
    i4_mode = property(None, lambda self, val: self.input_set_mode('I4', val))
    i5_mode = property(None, lambda self, val: self.input_set_mode('I5', val))
    i6_mode = property(None, lambda self, val: self.input_set_mode('I6', val))
    i7_mode = property(None, lambda self, val: self.input_set_mode('I7', val))
    i8_mode = property(None, lambda self, val: self.input_set_mode('I8', val))

    c1_mode = property(None, lambda self, val: self.counter_set_mode('C1', val))
    c2_mode = property(None, lambda self, val: self.counter_set_mode('C2', val))
    c3_mode = property(None, lambda self, val: self.counter_set_mode('C3', val))
    c4_mode = property(None, lambda self, val: self.counter_set_mode('C4', val))

    m1_counter_brake = property(None, lambda self, val: self._set_motor_counter_brake('M1', val))
    m2_counter_brake = property(None, lambda self, val: self._set_motor_counter_brake('M2', val))
    m3_counter_brake = property(None, lambda self, val: self._set_motor_counter_brake('M3', val))
    m4_counter_brake = property(None, lambda self, val: self._set_motor_counter_brake('M4', val))


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
    :return: The path of the ftDuino or ``None`` if the ftDuino was not found.
    """
    for path, device_name in ftduino_iter():
        if device_name == name:
            return path
    return None
