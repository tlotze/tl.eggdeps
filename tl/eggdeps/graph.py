# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

import sys
import pkg_resources


def graph_from_requirements(requirement_strings, ignored, is_dead_end):
    ws = pkg_resources.working_set
    requirements = set(pkg_resources.Requirement.parse(req)
                       for req in requirement_strings)
    roots = names(requirements, ignored)
    nodes = {}

    def add_requirement(req):
        name = req.project_name
        if ignored(name):
            return
        if is_dead_end(name):
            nodes[name] = {}
            return

        dist = pkg_resources.get_distribution(req)
        plain_reqs = set(dist.requires())
        extra_reqs = set(dist.requires(req.extras)) - plain_reqs

        plain_names = names(plain_reqs, ignored)
        if name in nodes:
            nodes[name]["extra"].update(
                names(extra_reqs, ignored) - plain_names)
        else:
            nodes[name] = {None: plain_names,
                           "extra": names(extra_reqs, ignored) - plain_names,
                           }
            for req in plain_reqs:
                add_requirement(req)

        for req in extra_reqs:
            add_requirement(req)

    for req in requirements:
        add_requirement(req)

    return roots, nodes


def graph_from_working_set(ignored, is_dead_end):
    ws = pkg_resources.working_set
    roots = names(ws, ignored)
    nodes = {}

    for dist in ws:
        name = dist.project_name
        if ignored(name):
            return

        all_names = names(dist.requires(dist.extras), ignored)
        roots -= all_names

        if name in dead_ends:
            nodes[name] = {}
            return

        plain_names = names(dist.requires(), ignored)
        nodes[name] = {None: plain_names,
                       "extra": all_names - plain_names,
                       }

    return roots, nodes


def names(collection, ignored=None):
    return set(item.project_name for item in collection
               if not ignored(item.project_name))
