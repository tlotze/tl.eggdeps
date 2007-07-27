# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

import optparse

import tl.eggdeps.graph
import tl.eggdeps.dot
import tl.eggdeps.plaintext


def eggdeps():
    parser = optparse.OptionParser("usage: %prog [options] [requirements]")
    parser.add_option("-i", "--ignore",
                      dest="ignore", action="append", default=[],
                      help="project names to ignore")
    parser.add_option("-d", "--dot",
                      dest="dot", action="store_true", default=False,
                      help="whether to produce a dot file")
    options, requirements = parser.parse_args()

    if requirements:
        graph = tl.eggdeps.graph.graph_from_requirements(requirements)
    else:
        graph = tl.eggdeps.graph.graph_from_working_set()

    tl.eggdeps.graph.filter_graph(graph, options)

    if options.dot:
        tl.eggdeps.dot.print_dot(graph)
    else:
        tl.eggdeps.plaintext.print_graph(graph)
