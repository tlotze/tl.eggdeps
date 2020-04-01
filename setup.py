#!/usr/bin/env python
"""Compute a dependency graph between active Python eggs.
"""

from setuptools import setup, find_packages


longdesc = "\n\n".join((open("README.rst").read(),
                        open("ABOUT.rst").read()))

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
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Software Development",
    "Topic :: Utilities",
]

setup(name="tl.eggdeps",
      version='1.0',
      description=__doc__.strip(),
      long_description=longdesc,
      keywords="egg eggs dependencies dependency graph tree",
      classifiers=classifiers,
      author="Thomas Lotze",
      author_email="thomas@thomas-lotze.de",
      url="https://github.com/tlotze/tl.eggdeps",
      license="ZPL 2.1",
      packages=find_packages('src'),
      package_dir={'': 'src'},
      entry_points=entry_points,
      python_requires='>=3.7, <4',
      install_requires=install_requires,
      extras_require=extras_require,
      tests_require=tests_require,
      include_package_data=True,
      test_suite="tl.eggdeps.tests.test_suite",
      namespace_packages=["tl"],
      zip_safe=False,
      )
