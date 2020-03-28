from __future__ import print_function
import doctest
from doctest import DocTestSuite, DocFileSuite
import os.path
import pkg_resources
import tl.eggdeps.requirements
import unittest


class Metadata(pkg_resources.EmptyProvider):
    """Mock object to return metadata as if from an on-disk distribution"""

    def __init__(self, *pairs):
        self.metadata = dict(pairs)

    def has_metadata(self, name):
        return name in self.metadata

    def get_metadata(self, name):
        return self.metadata[name]

    def get_metadata_lines(self, name):
        return pkg_resources.yield_lines(self.get_metadata(name))


def make_dist(filename, depends=""):
    metadata = Metadata(("depends.txt", depends))
    return pkg_resources.Distribution.from_filename(filename,
                                                    metadata=metadata)


def make_working_set(*dists):
    ws = pkg_resources.WorkingSet([])
    for dist in dists:
        ws.add(dist)
    return ws


def _sprint(value):
    if isinstance(value, set):
        if len(value):
            return "{{{}}}".format(", ".join(repr(elem) for elem in sorted(value)))
        else:
            return "set()"
    if isinstance(value, dict):
        return "{%s}" % ", ".join("%r: %s" % (key, _sprint(value))
                                  for key, value in sorted(value.items()))
    if isinstance(value, list):
        return "[{}]".format(", ".join(_sprint(v) for v in value))
    if isinstance(value, tuple):
        return "({})".format(", ".join(_sprint(v) for v in value))
    return repr(value)


def sprint(value):
    print(_sprint(value))


def sort_specs(specs):
    return sorted(specs, key=lambda x: x.project_name)


class Options(dict):

    version_numbers = False
    once = False
    terse = False
    cluster = False
    version_specs = False

    def __init__(self, *args, **kwargs):
        self.__dict__ = self
        super(Options, self).__init__(*args, **kwargs)


def test_suite():
    return unittest.TestSuite([
        DocTestSuite(tl.eggdeps.requirements)
        ] + [
        DocFileSuite(filename,
                     package="tl.eggdeps",
                     globs=dict(make_dist=make_dist,
                                make_working_set=make_working_set,
                                sprint=sprint,
                                sort_specs=sort_specs,
                                Options=Options,
                                ),
                     optionflags=doctest.NORMALIZE_WHITESPACE |
                                 (0 if filename == 'plaintext.txt'
                                  else doctest.ELLIPSIS) |
                                 doctest.REPORT_NDIFF,
                     )
        for filename in sorted(os.listdir(os.path.dirname(__file__)))
        if filename.endswith(".txt")
        ])
