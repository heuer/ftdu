ftdu - Talk to ftDuino via Python
=================================

ftdu can be used as client for the ```ftduino_direct``` sketch.

It provides a more pythonic API to communicate with a ftDuino.


Installation
------------
Install the ftduino_direct sketch, see <https://github.com/heuer/ftduino_direct#installation>


Use ``pip`` to install ftdu::

    $ pip install git+https://github.com/heuer/ftdu.git@develop


Usage
-----

Library
^^^^^^^

.. code-block:: python

    >>> import ftdu
    >>> ftd = ftdu.FtDuino()
    >>> ftd.led = True  # Switch the LED on
