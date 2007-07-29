# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

import unittest
import doctest
from zope.testing.doctest import DocFileSuite


flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

def test_suite():
    return unittest.TestSuite((
        DocFileSuite("graph.txt", package="tl.eggdeps", optionflags=flags),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
