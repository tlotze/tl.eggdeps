# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

import re
import optparse

import tl.eggdeps.graph
import tl.eggdeps.dot
import tl.eggdeps.plaintext


def eggdeps():
    parser = optparse.OptionParser("usage: %prog [options] [requirements]")
    parser.add_option("-i", "--ignore",
                      dest="ignore", action="append", default=[],
                      help="project names to ignore")
    parser.add_option("-I", "--re-ignore",
                      dest="re_ignore", action="append", default=[],
                      help="project name pattern to ignore")
    parser.add_option("-e", "--dead-end",
                      dest="dead_ends", action="append", default=[],
                      help="names of projects whose dependencies to ignore")
    parser.add_option("-E", "--re-dead-end",
                      dest="re_dead_ends", action="append", default=[],
                      help="name patterns of projects "
                           "whose dependencies to ignore")
    parser.add_option("-d", "--dot",
                      dest="dot", action="store_true", default=False,
                      help="whether to produce a dot file")
    options, requirements = parser.parse_args()

    ignored = matcher(options.ignore, options.re_ignore)
    is_dead_end = matcher(options.dead_ends, options.re_dead_ends)

    if requirements:
        graph = tl.eggdeps.graph.graph_from_requirements(
            requirements, ignored, is_dead_end)
    else:
        graph = tl.eggdeps.graph.graph_from_working_set(ignored, is_dead_end)

    if options.dot:
        tl.eggdeps.dot.print_dot(graph, is_dead_end)
    else:
        tl.eggdeps.plaintext.print_graph(graph, is_dead_end)


def matcher(names, patterns):
    names = set(names)
    compiled_patterns = [re.compile(pattern) for pattern in patterns]

    def match(name):
        if name in names:
            return True

        for re in compiled_patterns:
            if re.search(name):
                return True

        return False

    return match
