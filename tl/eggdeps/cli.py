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
    parser.add_option("-e", "--deadend",
                      dest="dead_ends", action="append", default=[],
                      help="names of projects whose dependencies to ignore")
    parser.add_option("-d", "--dot",
                      dest="dot", action="store_true", default=False,
                      help="whether to produce a dot file")
    options, requirements = parser.parse_args()

    kwargs = dict(ignore=options.ignore,
                  dead_ends=options.dead_ends,
                  )

    if requirements:
        graph = tl.eggdeps.graph.graph_from_requirements(requirements, **kwargs)
    else:
        graph = tl.eggdeps.graph.graph_from_working_set(**kwargs)

    if options.dot:
        tl.eggdeps.dot.print_dot(graph, **kwargs)
    else:
        tl.eggdeps.plaintext.print_graph(graph, **kwargs)
