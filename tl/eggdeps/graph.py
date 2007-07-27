# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

import pkg_resources


def graph_from_requirements(requirement_strings):
    ws = pkg_resources.working_set
    requirements = set(pkg_resources.Requirement.parse(req)
                       for req in requirement_strings)
    roots = names(requirements)
    nodes = {}

    def add_requirement(req):
        name = req.project_name
        dist = pkg_resources.get_distribution(req)
        plain_reqs = set(dist.requires())
        extra_reqs = set(dist.requires(req.extras)) - plain_reqs

        plain_names = names(plain_reqs)
        if name in nodes:
            nodes[name]["extra"].update(names(extra_reqs) - plain_names)
        else:
            nodes[name] = {None: plain_names,
                           "extra": names(extra_reqs) - plain_names,
                           }
            for req in plain_reqs:
                add_requirement(req)

        for req in extra_reqs:
            add_requirement(req)

    for req in requirements:
        add_requirement(req)

    return roots, nodes


def graph_from_working_set():
    ws = pkg_resources.working_set
    roots = names(ws)
    nodes = {}

    for dist in ws:
        name = dist.project_name

        all_names = names(dist.requires(dist.extras))
        roots -= all_names

        plain_names = names(dist.requires())
        nodes[name] = {None: plain_names,
                       "extra": all_names - plain_names,
                       }

    return roots, nodes


def filter_graph(graph, options):
    roots, nodes = graph
    ignore = set(options.ignore)

    roots -= ignore

    for name, links in nodes.items():
        if name in ignore:
            del nodes[name]
            continue

        for link_type, targets in links.items():
            targets -= ignore
            if not targets:
                del links[link_type]


def names(collection):
    return set(item.project_name for item in collection)
