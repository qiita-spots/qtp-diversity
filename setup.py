#!/usr/bin/env python

# -----------------------------------------------------------------------------
# Copyright (c) 2013, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
from setuptools import setup
from glob import glob

__version__ = "2023.02"

classes = """
    Development Status :: 3 - Alpha
    License :: OSI Approved :: BSD License
    Topic :: Scientific/Engineering :: Bio-Informatics
    Topic :: Software Development :: Libraries :: Application Frameworks
    Topic :: Software Development :: Libraries :: Python Modules
    Programming Language :: Python
    Programming Language :: Python :: 3.5
    Programming Language :: Python :: Implementation :: CPython
    Operating System :: POSIX :: Linux
    Operating System :: MacOS :: MacOS X
"""

with open('README.rst') as f:
    long_description = f.read()

classifiers = [s.strip() for s in classes.split('\n') if s]

setup(name='qtp_diversity',
      version=__version__,
      long_description=long_description,
      license="BSD",
      description='Qiita Type Plugin: diversity',
      author="Qiita development team",
      author_email="qiita.help@gmail.com",
      url='https://github.com/qiita-spots/qtp-diversity',
      test_suite='nose.collector',
      packages=['qtp_diversity'],
      scripts=glob('scripts/*'),
      install_requires=['click', 'scikit-bio', 'pandas', 'numpy', 'emperor',
                        'qiita-files @ https://github.com/'
                        'qiita-spots/qiita-files/archive/master.zip',
                        'qiita_client @ https://github.com/qiita-spots/'
                        'qiita_client/archive/master.zip'],
      classifiers=classifiers
      )
