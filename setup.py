#!/usr/bin/env python
#
# Copyright (c) 2007-2009 Thomas Lotze
# See also LICENSE.txt

"""Compute a dependency graph between active Python eggs.
"""

import os.path
import glob
from setuptools import setup, find_packages


project_path = lambda *names: os.path.join(os.path.dirname(__file__), *names)

longdesc = "\n\n".join((open(project_path("README.txt")).read(),
                        open(project_path("ABOUT.txt")).read()))

root_files = glob.glob(project_path("*.txt"))
data_files = [("", [name for name in root_files
                    if os.path.split(name)[1] != "index.txt"])]

entry_points = {
    "console_scripts": [
    "eggdeps = tl.eggdeps.cli:eggdeps",
    ],
    }

install_requires = [
    "setuptools",
    ]

tests_require = [
    "zope.testing",
    ]

extras_require = {
    "test": tests_require,
    }

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Zope Public License",
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Topic :: Utilities",
    ]

setup(name="tl.eggdeps",
      version="0.4dev",
      description=__doc__.strip(),
      long_description=longdesc,
      keywords="egg eggs dependencies dependency graph tree",
      classifiers=classifiers,
      author="Thomas Lotze",
      author_email="thomas@thomas-lotze.de",
      url="http://thomas-lotze.de/en/software/eggdeps/",
      license="ZPL 2.1",
      packages=find_packages(),
      entry_points=entry_points,
      install_requires=install_requires,
      extras_require=extras_require,
      tests_require=tests_require,
      include_package_data=True,
      data_files=data_files,
      test_suite="tl.eggdeps.tests.test_suite",
      namespace_packages=["tl"],
      zip_safe=False,
      )
