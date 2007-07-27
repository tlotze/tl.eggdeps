# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt


def print_subgraph(root, graph, shortest, has_tree, printed,
                   link_type=None, depth=0):
    print_tree = depth == shortest[root] and root not in printed
    line = depth*"    " + root
    if link_type:
        line += " (%s)" % link_type
    if not print_tree and root in has_tree:
        line += " ..."
    if graph.is_dead_end(root):
        line += " *"
    print line

    if not print_tree:
        return
    printed.add(root)

    links = graph.get(root, {})
    for link_type, targets in sorted(links.iteritems()):
        for target in sorted(targets):
            print_subgraph(target, graph, shortest, has_tree, printed,
                           link_type, depth + 1)


def prepare(root, graph, shortest, has_tree, depth=0):
    if root in shortest and shortest[root] <= depth:
        return
    shortest[root] = depth
    links = graph.get(root, {})
    for link_type, targets in links.iteritems():
        for target in sorted(targets):
            has_tree.add(root)
            prepare(target, graph, shortest, has_tree, depth + 1)


def print_graph(graph):
    shortest = {}
    has_tree = set()
    for root in graph.roots:
        prepare(root, graph, shortest, has_tree)
    printed = set()

    for root in sorted(graph.roots):
        print_subgraph(root, graph, shortest, has_tree, printed)
