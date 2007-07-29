# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt


def print_dot(graph, cluster=False):
    direct_deps = set()
    for name in graph.roots:
        direct_deps.update(graph[name])

    print "digraph {"

    for node in graph.itervalues():
        node_options = dict(label=node.name)

        def fill(color):
            node_options["style"] = "filled"
            node_options["fillcolor"] = color
        if node.name in direct_deps:
            fill("yellow")
        if node.name in graph.roots:
            fill("green")
        if not node.follow:
            fill("lightgrey")
        if not node.dist:
            fill("red")

        print node.name.replace(".", "_") + format_options(node_options)

    if cluster:
        for i, cluster in enumerate(yield_clusters(graph)):
            print "subgraph cluster_%s {" % i
            for name in cluster:
                print name.replace(".", "_")
            print "}"

    for node in graph.itervalues():
        for dep, extras in node.iteritems():
            edge_options = {}
            if extras:
                edge_options["color"] = "lightgrey"

            print "%s -> %s%s" % (node.name.replace(".", "_"),
                                  dep.replace(".", "_"),
                                  format_options(edge_options))

    print "}"


def format_options(options):
    if not options:
        return ""

    return " [%s]" % ", ".join('%s="%s"' % item
                               for item in options.iteritems())


def yield_clusters(graph):
    clusters = [set(graph[name]).union((name,)) for name in graph.roots]
    while clusters:
        cluster = clusters.pop()
        for other in reversed(clusters):
            if cluster & other:
                cluster |= other
                clusters.remove(other)
        yield cluster
