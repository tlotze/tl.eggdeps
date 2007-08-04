# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt


def print_subgraph(graph, mount_points, path, print_version=False):
    name = path[-1]
    print_tree = path == mount_points[name]
    root = graph[name]

    if print_version and root.dist:
        name_string = "%s %s" % (root.name, root.dist.version)
    else:
        name_string = root.name

    line = prefix = (len(path) - 1) * "    "
    if root.compatible:
        line += name_string
    else:
        line += "(%s)" % name_string
    if not print_tree and root:
        line += " ..."
    if not root.follow:
        line += " *"
    print line

    if not print_tree:
        return

    last_extras = ()
    for extras, dep in sorted((sorted(extras), dep)
                              for dep, extras in root.iteritems()):
        if extras and extras != last_extras:
            print prefix + "  [%s]" % ','.join(extras)
            last_extras = extras

        print_subgraph(graph, mount_points, path + (dep,),
                       print_version=print_version)


def find_mount_point(graph, mount_points, extras_key, path, path_extras):
    name = path[-1]
    if (name in mount_points and
        (extras_key[name], mount_points[name]) <= (path_extras, path)):
        return

    mount_points[name] = path
    extras_key[name] = path_extras

    for dep, extras in graph[name].iteritems():
        find_mount_point(graph, mount_points, extras_key,
                         path + (dep,), path_extras + (sorted(extras),))


def print_graph(graph, print_version=False):
    mount_points = {}
    extras_key = {}
    for name in graph.roots:
        find_mount_point(graph, mount_points, extras_key, (name,), ((),))

    for name in sorted(graph.roots):
        print_subgraph(graph, mount_points, (name,),
                       print_version=print_version)
