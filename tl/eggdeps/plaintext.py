# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt


def print_subgraph(graph, mount_points, path, print_version=False):
    name = path[-1]
    print_tree = path == mount_points[name]
    node = graph[name]

    if print_version and node.dist:
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

        print_subgraph(graph, mount_points, path + (dep,),
                       print_version=print_version)


def find_mount_point(graph, mount_points, best_keys, path, sort_key):
    name = path[-1]
    if (name in mount_points and
        (best_keys[name], mount_points[name]) <= (sort_key, path)):
        return

    mount_points[name] = path
    best_keys[name] = sort_key

    for dep, extras in graph[name].iteritems():
        find_mount_point(graph, mount_points, best_keys,
                         path + (dep,), sort_key + (sorted(extras),))


def print_graph(graph, print_version=False):
    mount_points = {}
    best_keys = {}
    for name in graph.roots:
        find_mount_point(graph, mount_points, best_keys, (name,), ((),))

    for name in sorted(graph.roots):
        print_subgraph(graph, mount_points, (name,),
                       print_version=print_version)
