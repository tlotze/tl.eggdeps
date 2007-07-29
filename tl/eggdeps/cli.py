# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

import re
import optparse

import tl.eggdeps.graph
import tl.eggdeps.dot
import tl.eggdeps.plaintext


def eggdeps():
    parser = optparse.OptionParser("usage: %prog [options] [specifications]")
    parser.add_option("-i", "--ignore",
                      dest="ignore", action="append", default=[],
                      help="project names to ignore")
    parser.add_option("-I", "--re-ignore",
                      dest="re_ignore", action="append", default=[],
                      help="regular expression for project names to ignore")
    parser.add_option("-e", "--dead-end",
                      dest="dead_ends", action="append", default=[],
                      help="names of projects whose dependencies to ignore")
    parser.add_option("-E", "--re-dead-end",
                      dest="re_dead_ends", action="append", default=[],
                      help="regular expression for project names "
                           "whose dependencies to ignore")
    parser.add_option("-n", "--no-extras",
                      dest="extras", action="store_false", default=True,
                      help="always omit extra dependencies")
    parser.add_option("-d", "--dot",
                      dest="dot", action="store_true", default=False,
                      help="produce a dot graph")
    parser.add_option("-c", "--cluster",
                      dest="cluster", action="store_true", default=False,
                      help="in a dot graph, cluster direct dependencies "
                           "of each root distribution")
    options, specifications = parser.parse_args()

    show = unmatcher(options.ignore, options.re_ignore)
    follow = unmatcher(options.dead_ends, options.re_dead_ends)

    graph = tl.eggdeps.graph.Graph(show=show,
                                   follow=follow,
                                   extras=options.extras,
                                   )

    if specifications:
        graph.from_specifications(*specifications)
    else:
        graph.from_working_set()

    if options.dot:
        tl.eggdeps.dot.print_dot(graph, cluster=options.cluster)
    else:
        tl.eggdeps.plaintext.print_graph(graph)


def unmatcher(names, patterns):
    names = set(names)
    compiled_patterns = [re.compile(pattern) for pattern in patterns]

    def unmatch(name):
        if name in names:
            return False

        for re in compiled_patterns:
            if re.search(name):
                return False

        return True

    return unmatch
