# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt


def print_dot(graph):
    print "digraph {"

    for node in graph.itervalues():
        node_options = dict(label=node.name)
        if not node.is_active:
            node_options["color"] = "lightgrey"
        if node.name in graph.roots:
            node_options["style"] = "filled"
            node_options["fillcolor"] = "green"
        if node.is_dead_end:
            node_options["style"] = "filled"
        print node.name.replace(".", "_") + format_options(node_options)

        for target, link_type in node.iteritems():
            edge_options = {}
            if link_type:
                edge_options["color"] = "lightgrey"

            print "%s -> %s%s" % (node.name.replace(".", "_"),
                                  target.replace(".", "_"),
                                  format_options(edge_options))

    print "}"


def format_options(options):
    if not options:
        return ""

    return " [%s]" % ", ".join('%s="%s"' % item
                               for item in options.iteritems())
