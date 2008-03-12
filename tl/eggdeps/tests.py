# Copyright (c) 2007-2008 Thomas Lotze
# See also LICENSE.txt

import os.path
import unittest
import doctest
from zope.testing.doctest import DocFileSuite

import pkg_resources
import setuptools.tests.test_resources


def make_dist(filename, depends=""):
    metadata = setuptools.tests.test_resources.Metadata(("depends.txt",
                                                         depends))
    return pkg_resources.Distribution.from_filename(filename,
                                                    metadata=metadata)


def make_working_set(*dists):
    ws = pkg_resources.WorkingSet([])
    for dist in dists:
        ws.add(dist)
    return ws


def _sprint(value):
    if isinstance(value, set):
        return "set([%s])" % ", ".join(repr(elem) for elem in sorted(value))
    if isinstance(value, dict):
        return "{%s}" % ", ".join("%r: %s" % (key, _sprint(value))
                                  for key, value in sorted(value.iteritems()))
    return repr(value)


def sprint(value):
    print _sprint(value)


def sort_specs(specs):
    return sorted(specs, cmp=lambda a, b: cmp(a.project_name, b.project_name))


def test_suite():
    return unittest.TestSuite([
        DocFileSuite(filename,
                     package="tl.eggdeps",
                     globs=dict(make_dist=make_dist,
                                make_working_set=make_working_set,
                                sprint=sprint,
                                sort_specs=sort_specs,
                                ),
                     optionflags=doctest.NORMALIZE_WHITESPACE |
                                 doctest.ELLIPSIS,
                     )
        for filename in sorted(os.listdir(os.path.dirname(__file__)))
        if filename.endswith(".txt")
        ])
