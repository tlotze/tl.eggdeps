# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

import pkg_resources


def graph_from_requirements(requirement_strings, ignore=(), dead_ends=(),
                            **kwargs):
    ignore = set(ignore)
    ws = pkg_resources.working_set
    requirements = set(pkg_resources.Requirement.parse(req)
                       for req in requirement_strings)
    roots = names(requirements) - ignore
    nodes = {}

    def add_requirement(req):
        name = req.project_name
        if name in ignore:
            return
        if name in dead_ends:
            nodes[name] = {}
            return

        dist = pkg_resources.get_distribution(req)
        plain_reqs = set(dist.requires())
        extra_reqs = set(dist.requires(req.extras)) - plain_reqs

        plain_names = names(plain_reqs)
        if name in nodes:
            nodes[name]["extra"].update(
                names(extra_reqs) - plain_names - ignore)
        else:
            nodes[name] = {None: plain_names - ignore,
                           "extra": names(extra_reqs) - plain_names - ignore,
                           }
            for req in plain_reqs:
                add_requirement(req)

        for req in extra_reqs:
            add_requirement(req)

    for req in requirements:
        add_requirement(req)

    return roots, nodes


def graph_from_working_set(ignore=(), dead_ends=(), **kwargs):
    ignore = set(ignore)
    ws = pkg_resources.working_set
    roots = names(ws) - ignore
    nodes = {}

    for dist in ws:
        name = dist.project_name
        if name in ignore:
            return

        all_names = names(dist.requires(dist.extras))
        roots -= all_names

        if name in dead_ends:
            nodes[name] = {}
            return

        plain_names = names(dist.requires())
        nodes[name] = {None: plain_names - ignore,
                       "extra": all_names - plain_names - ignore,
                       }

    return roots, nodes


def names(collection):
    return set(item.project_name for item in collection)
