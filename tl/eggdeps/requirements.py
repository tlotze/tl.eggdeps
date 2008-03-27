# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

import pprint

import pkg_resources


def print_list(graph, options):
    """Print a requirements list to standard output.

    graph: a tl.eggdeps.graph.Graph instance

    options: an object that provides formatting options as attributes

        version_numbers: bool, print version numbers of active distributions?
    """
    reqs = []
    for name, node in sorted(graph.iteritems()):
        if options.version_numbers:
            reqs.append(node.dist.as_requirement())
        else:
            reqs.append(pkg_resources.Requirement.parse(name))

    pprint.pprint([str(req) for req in reqs])
