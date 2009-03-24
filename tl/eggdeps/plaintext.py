# Copyright (c) 2007-2008 Thomas Lotze
# See also LICENSE.txt


def print_subgraph(graph, mount_points, path, options):
    name = path[-1]
    print_tree = path == mount_points[name]

    if options.once and not print_tree:
        return False

    node = graph[name]

    if options.version_numbers and node.dist:
        name_string = "%s %s" % (node.name, node.dist.version)
    else:
        name_string = node.name

    line = prefix = (len(path) - 1) * "    "
    if node.compatible:
        line += name_string
    else:
        line += "(%s)" % name_string
    if not options.terse and not print_tree and node:
        line += " ..."
    if not node.follow:
        line += " *"
    print line

    if not print_tree:
        return False

    last_extras = []
    printed_all = True
    for extras, dep in sorted((sorted(extras), dep)
                              for dep, extras in node.iteritems()):
        # XXX If options.terse, extras whose dependencies will not be printed
        # should not be printed themselves. This requires rewriting most of
        # this module to calculate all output before printing anything.
        if extras != last_extras:
            print prefix + "  [%s]" % ','.join(extras)
            last_extras = extras

        printed_all = (print_subgraph(graph, mount_points,
                                      path + (dep,), options)
                       and printed_all)

    if options.once and not options.terse and not printed_all:
        print prefix + "    ..."

    return True


def find_mount_point(graph, mount_points, best_keys, path, sort_key):
    name = path[-1]
    if name in mount_points and best_keys[name] <= sort_key:
        return

    mount_points[name] = path
    best_keys[name] = sort_key

    for dep, extras in graph[name].iteritems():
        find_mount_point(graph, mount_points, best_keys, path + (dep,),
                         (sort_key[0] + (bool(extras),),
                          sort_key[1] + (sorted(extras), name)))


def print_graph(graph, options):
    """Print a dependency graph to standard output as plain text.

    graph: a tl.eggdeps.graph.Graph instance

    options: an object that provides formatting options as attributes

        version_numbers: bool, print version numbers of active distributions?
    """
    mount_points = {}
    best_keys = {}
    for name in graph.roots:
        find_mount_point(graph, mount_points, best_keys, (name,),
                         ((False,), ((), name)))

    for name in sorted(graph.roots):
        print_subgraph(graph, mount_points, (name,), options)
