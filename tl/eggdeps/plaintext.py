# Copyright (c) 2007-2009 Thomas Lotze
# See also LICENSE.txt


def print_subgraph(graph, mount_points, path, seen, options):
    name = path[-1]
    print_tree = (path == mount_points[name] and name not in seen)

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

    deps_by_extra = {None: set()}
    for dep, extras in node.iter_deps():
        if extras:
            for extra in extras:
                deps_by_extra.setdefault(extra, set()).add(dep)
        else:
            deps_by_extra[None].add(dep)

    printed_all = True
    seen = set()
    for extra, deps in sorted(deps_by_extra.items()):
        # XXX If options.terse, extras whose dependencies will not be printed
        # should not be printed themselves. This requires rewriting most of
        # this module to calculate all output before printing anything.
        if extra:
            print prefix + "  [%s]" % extra

        for dep in sorted(deps):
            printed_all = (print_subgraph(graph, mount_points,
                                          path + (dep,), seen, options)
                           and printed_all)
            seen.add(dep)

    if options.once and not options.terse and not printed_all:
        print prefix + "    ..."

    return True


def find_mount_point(graph, mount_points, best_keys, path, sort_key):
    name = path[-1]
    if name in mount_points and best_keys[name] <= sort_key:
        return

    mount_points[name] = path
    best_keys[name] = sort_key

    for dep, extras in graph[name].iter_deps():
        find_mount_point(graph, mount_points, best_keys, path + (dep,),
                         sort_key + (bool(extras),))


def print_graph(graph, options):
    """Print a dependency graph to standard output as plain text.

    graph: a tl.eggdeps.graph.Graph instance

    options: an object that provides formatting options as attributes

        version_numbers: bool, print version numbers of active distributions?
    """
    mount_points = {}
    best_keys = {}
    for name in graph.roots:
        find_mount_point(graph, mount_points, best_keys, (name,), (False,))

    for name in sorted(graph.roots):
        print_subgraph(graph, mount_points, (name,), set(), options)
