# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt


def print_subgraph(root, shortest, has_tree, printed, nodes,
                   link_type=None, depth=0):
    print_tree = depth == shortest[root] and root not in printed
    if print_tree or root not in has_tree:
        ellipsis = ""
    else:
        ellipsis = " ..."
    if link_type:
        link_prefix = " (%s)" % link_type
    else:
        link_prefix = ""
    print depth*"    " + root + link_prefix + ellipsis

    if not print_tree:
        return
    printed.add(root)

    links = nodes.get(root, {})
    for link_type, targets in sorted(links.iteritems()):
        for target in sorted(targets):
            print_subgraph(target, shortest, has_tree, printed, nodes,
                           link_type, depth + 1)


def prepare(root, nodes, shortest, has_tree, depth=0):
    if root in shortest and shortest[root] <= depth:
        return
    shortest[root] = depth
    links = nodes.get(root, {})
    for link_type, targets in links.iteritems():
        for target in sorted(targets):
            has_tree.add(root)
            prepare(target, nodes, shortest, has_tree, depth + 1)


def print_graph(graph):
    roots, nodes = graph

    shortest = {}
    has_tree = set()
    for root in roots:
        prepare(root, nodes, shortest, has_tree)
    printed = set()

    for root in roots:
        print_subgraph(root, shortest, has_tree, printed, nodes)
