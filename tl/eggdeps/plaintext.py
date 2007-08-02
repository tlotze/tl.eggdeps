# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt


def print_subgraph(name, graph, mount_points, extras=None, path=(),
                   print_version=False):
    print_tree = path == mount_points[name]
    root = graph[name]

    if print_version and root.dist:
        name_string = "%s %s" % (root.name, root.dist.version)
    else:
        name_string = root.name

    line = len(path) * "    "
    if root.compatible:
        line += name_string
    else:
        line += "(%s)" % name_string
    if extras:
        line += " [%s]" % ','.join(extras)
    if not print_tree and root:
        line += " ..."
    if not root.follow:
        line += " *"
    print line

    if not print_tree:
        return

    for extras, dep in sorted((sorted(extras), dep)
                              for dep, extras in root.iteritems()):
        print_subgraph(dep, graph, mount_points, extras, path + (name,),
                       print_version=print_version)


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


def print_graph(graph, print_version=False):
    mount_points = {}
    plain_mounts = set()
    for name in graph.roots:
        find_mount_point(name, graph, mount_points, plain_mounts)

    for name in sorted(graph.roots):
        print_subgraph(name, graph, mount_points,
                       print_version=print_version)
