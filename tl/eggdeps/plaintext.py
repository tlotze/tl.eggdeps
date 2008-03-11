# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt


def print_subgraph(graph, mount_points, path, options):
    name = path[-1]
    print_tree = path == mount_points[name]
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
    if not print_tree and node:
        line += " ..."
    if not node.follow:
        line += " *"
    print line

    if not print_tree:
        return

    last_extras = []
    for extras, dep in sorted((sorted(extras), dep)
                              for dep, extras in node.iteritems()):
        if extras != last_extras:
            print prefix + "  [%s]" % ','.join(extras)
            last_extras = extras

        print_subgraph(graph, mount_points, path + (dep,), options)


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
