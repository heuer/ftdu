ftdu - Talk to ftDuino via Python
=================================

ftdu can be used as client for the ```ftduino_direct``` sketch.

It provides a more pythonic API to communicate with a ftDuino.


Installation
------------
Install the ftduino_direct sketch, see <https://github.com/PeterDHabermehl/ftduino_direct#installation>


Use ``pip`` to install ftdu::

    $ pip install ftdu


Usage
-----

Library
^^^^^^^

.. code-block:: python

    >>> import ftdu
    >>> ftd = ftdu.FtDuino()
    >>> ftd.led = True  # Switch the LED on
    >>> ftd.o1 = True  # Enable O1
    >>> ftd.i1  # Ask value of input port I1
    0
    >>> ftd.close()

