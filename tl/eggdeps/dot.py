# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt


def print_dot(graph, is_dead_end):
    roots, nodes = graph

    print "digraph {"

    for name, links in nodes.iteritems():
        node_options = dict(label=name)
        if name in roots:
            node_options["style"] = "filled"
            node_options["fillcolor"] = "green"
        if is_dead_end(name):
            node_options["style"] = "filled"
        print name.replace(".", "_") + format_options(node_options)

        for link_type, targets in links.iteritems():
            edge_options = {}
            if link_type is 'extra':
                edge_options["color"] = "lightgrey"

            for target in targets:
                print "%s -> %s%s" % (name.replace(".", "_"),
                                      target.replace(".", "_"),
                                      format_options(edge_options))

    print "}"


def format_options(options):
    if not options:
        return ""

    return " [%s]" % ", ".join('%s="%s"' % item
                               for item in options.iteritems())
