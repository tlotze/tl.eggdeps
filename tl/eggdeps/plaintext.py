# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt


def print_subgraph(name, graph, mount_points, link_type=None, path=()):
    print_tree = path == mount_points[name]
    root = graph[name]

    line = len(path) * "    "
    if root.is_active:
        line += name
    else:
        line += "(%s)" % name
    if link_type:
        line += " [%s]" % ','.join(sorted(link_type))
    if not print_tree and root:
        line += " ..."
    if root.is_dead_end:
        line += " *"
    print line

    if not print_tree:
        return

    for target, link_type in sorted(
        root.iteritems(),
        cmp=lambda (a, b), (c, d): cmp(sorted(b), sorted(d)) or cmp(a, c)):
        print_subgraph(target, graph, mount_points, link_type, path + (name,))


def find_mount_point(name, graph, mount_points, plain_mounts,
                     path=(), is_plain=True):
    # prefer paths without extra dependencies
    if name in plain_mounts and not is_plain:
        return

    mount_point = mount_points.get(name)
    if mount_point is not None:
        # prefer short paths
        if len(path) > len(mount_point):
            return
        # prefer alphabetically first among paths of equal length
        if len(path) == len(mount_point) and path > mount_point:
            return

    mount_points[name] = path
    if is_plain:
        plain_mounts.add(name)

    path += (name,)
    for dep, extras in graph[name].iteritems():
        find_mount_point(dep, graph, mount_points, plain_mounts,
                         path, is_plain and not extras)


def print_graph(graph):
    mount_points = {}
    plain_mounts = set()
    for name in graph.roots:
        find_mount_point(name, graph, mount_points, plain_mounts)

    for name in sorted(graph.roots):
        print_subgraph(name, graph, mount_points)
