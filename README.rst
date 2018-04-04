nut2
====

.. image:: https://travis-ci.org/rshipp/python-nut2.svg?branch=master
   :target: https://travis-ci.org/rshipp/python-nut2
   :alt: Build Status
.. image:: https://coveralls.io/repos/rshipp/python-nut2/badge.png?branch=master
   :target: https://coveralls.io/r/rshipp/python-nut2?branch=master
   :alt: Test Coverage
.. image:: https://api.codacy.com/project/badge/Grade/741acf61ed264ba3aac7dcf33c55a40f
   :target: https://www.codacy.com/app/rshipp/python-nut2
   :alt: Code Health
.. image:: http://img.shields.io/pypi/v/nut2.svg
   :target: https://pypi.python.org/pypi/nut2
   :alt: PyPi Version

This is an API overhaul of PyNUT_, a Python library to allow communication with NUT
(`Network UPS Tools`_) servers.

**Note**: This is an unofficial project, and is in no way supported or
endorsed by the `Network UPS Tools developers`_.

Requirements
------------

The module itself requires only Python (known to work with versions 2.6 through
3.4). If you wish to run the tests, do ``pip install -r requirements-testing.txt``.

Usage
-----

Example::

    from nut2 import PyNUTClient
    client = PyNUTClient()
    client.help()
    client.list_ups()
    client.list_vars("My_UPS")

Please note that this module has completely and intentionally broken
backwards compatibility with PyNUT 1.X.

See inline documentation for more usage information.

Installation
------------

Just use pip::

    pip install nut2

PyNUT
-----

The following information is copied from the original PyNUT README:

    This directory contains various NUT Client related Python scripts, written by
    David Goncalves, and released under GPL v3.

    * "module": this directory contains PyNUT.py, which is a Python abstraction
      class to access NUT server(s). You can use it in Python programs to access NUT's
      upsd data server in a simple way, without having to know the NUT protocol.

    To import it on Python programs you have to use the following (case sensitive) :
    'import PyNUT'

    This module provides a 'PyNUTClient' class that can be used to connect and get
    data from an upsd data server.

    To install the PyNUT module on Debian/Ubuntu, copy it to:
    /usr/share/python-support/python-pynut/

    This directory also contains test_nutclient.py, which is a PyNUT test program.
    For this to be fully functional, you will need to adapt the login, password and
    upsname to fit your configuration.


.. _PyNUT: https://github.com/networkupstools/nut/tree/master/scripts/python
.. _Network UPS Tools: http://www.networkupstools.org/
.. _Network UPS Tools developers: https://github.com/networkupstools
