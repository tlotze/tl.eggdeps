# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

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


def sort_specs(specs):
    return sorted(specs, cmp=lambda a, b: cmp(a.project_name, b.project_name))


def setUp(test):
    test.globs.update(dict(
        make_dist=make_dist,
        sort_specs=sort_specs,
        ))


def test_suite():
    return unittest.TestSuite([
        DocFileSuite(filename,
                     package="tl.eggdeps",
                     setUp=setUp,
                     optionflags=doctest.NORMALIZE_WHITESPACE |
                                 doctest.ELLIPSIS,
                     )
        for filename in (
        "graph.txt",
        )])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
