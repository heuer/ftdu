#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# License: BSD License
#
"""\
Setup script.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - http://www.semagia.com/
:license:      BSD License
"""
from __future__ import unicode_literals
from setuptools import setup, find_packages
import os
import io
import re


def read(*filenames, **kwargs):
    base_path = os.path.dirname(os.path.realpath(__file__))
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(os.path.join(base_path, filename), encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

version = re.search(r'''^__version__ = ["']([^'"]+)['"]''',
                    read('ftdu.py'), flags=re.MULTILINE).group(1)

setup(
    name='ftdu',
    version=version,
    url='https://github.com/heuer/ftdu/',
    description='Client to talk with ftDuino via USB ',
    long_description=read('README.rst', 'CHANGES.rst'),
    license='BSD',
    author='Lars Heuer',
    author_email='heuer@semagia.com',
    platforms=['any'],
    install_requires=['pyserial>=3.0'],
    packages=find_packages(exclude=['docs', 'tests', 'sandbox', 'htmlcov']),
    py_modules=['ftdu'],
    include_package_data=True,
    keywords=['fischertechnik', 'ftduino'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
