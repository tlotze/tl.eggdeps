#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

"""Eggs grow on trees. Dependency trees.
"""

import os, os.path
import glob
from setuptools import setup, find_packages


project_path = lambda *names: os.path.join(os.path.dirname(__file__), *names)


def include_tree(dest, source):
    source_len = len(source)
    for dirpath, dirnames, filenames in os.walk(source):
        yield (dest + dirpath[source_len:],
               [os.path.join(dirpath, fn) for fn in filenames])
        if ".svn" in dirnames:
            dirnames.remove(".svn")


longdesc = open(project_path("README.txt")).read()

data_files = [("", glob.glob(project_path("*.txt")))]

entry_points = {
    "console_scripts": [
    "eggdeps = tl.eggdeps.cli:eggdeps",
    ],
    }

install_requires = [
    "setuptools",
    ]

extras_require = {
    "test": ["zope.testing"],
    }

tests_require = [
    "zope.testing",
    ]

classifiers = [
    "Development Status :: 3 - Alpha",
    ]

setup(name="tl.eggdeps",
      version="trunk",
      description=__doc__.strip(),
      long_description=longdesc,
      keywords="egg eggs dependencies dependency graph tree",
      classifiers=classifiers,
      author="Thomas Lotze",
      author_email="thomas@thomas-lotze.de",
      url="http://www.thomas-lotze.de/en/software/eggdeps/",
      license="ZPL 2.1",
      packages=find_packages(),
      entry_points=entry_points,
      install_requires=install_requires,
      extras_require=extras_require,
      tests_require=tests_require,
      include_package_data=True,
      data_files=data_files,
      test_suite="tl.eggdeps.tests.test_suite",
      )
