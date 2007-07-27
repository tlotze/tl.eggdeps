# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt


def print_subgraph(name, graph, shortest, printed, link_type=None, depth=0):
    print_tree = depth == shortest[name] and name not in printed
    root = graph[name]
    line = depth*"    " + name
    if link_type:
        line += " [%s]" % ','.join(sorted(link_type))
    if not print_tree and root:
        line += " ..."
    if root.is_dead_end:
        line += " *"
    print line

    if not print_tree:
        return
    printed.add(name)

    for target, link_type in sorted(
        root.iteritems(),
        cmp=lambda (a, b), (c, d): cmp(sorted(b), sorted(d)) or cmp(a, c)):
        print_subgraph(target, graph, shortest, printed, link_type, depth + 1)


def prepare(name, graph, shortest, depth=0):
    if name in shortest and shortest[name] <= depth:
        return
    shortest[name] = depth

    for target in graph[name]:
        prepare(target, graph, shortest, depth + 1)


def print_graph(graph):
    shortest = {}
    for name in graph.roots:
        prepare(name, graph, shortest)
    printed = set()

    for name in sorted(graph.roots):
        print_subgraph(name, graph, shortest, printed)
