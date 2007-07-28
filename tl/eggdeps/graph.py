# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

import sys
import pkg_resources


class Graph(dict):
    """A graph of egg dependencies.
    """

    def __init__(self,
                 working_set=None,
                 ignored=lambda name: False,
                 is_dead_end=lambda name: False,
                 extras=True,
                 ):
        self.ignored = ignored
        self.is_dead_end = is_dead_end
        self.extras = extras
        self.working_set = working_set or pkg_resources.WorkingSet()
        self.roots = ()

    def from_specifications(self, specifications):
        requirements = set(pkg_resources.parse_requirements(specifications))
        self.roots = self.names(requirements)

        for req in self.filter(requirements):
            self.add_requirement(req)

    def add_requirement(self, req):
        node = self.setdefault(req.project_name, Node(self, req))
        if node.is_dead_end or not node.dist:
            return

        if not node:
            for dep in self.names(node.dist.requires()):
                node[dep] = set()

        new_reqs = set(node.dist.requires())
        if self.extras:
            plain_names = self.names(new_reqs)
            for extra in req.extras:
                extra_reqs = node.dist.requires((extra,))
                new_reqs |= extra_reqs
                for dep in self.names(extra_reqs) - plain_names:
                    node.setdefault(dep, set()).add(extra)

        new_reqs -= node.requirements
        node.requirements |= new_reqs
        for req in self.filter(new_reqs):
            self.add_requirement(req)

    def from_working_set(self):
        ws = self.filter(self.working_set)
        ws_names = self.names(ws)
        self.roots = ws_names.copy()

        for dist in ws:
            node = self[dist.project_name] = Node(self, dist)
            if node.is_dead_end:
                continue

            for dep in self.names(dist.requires()) & ws_names:
                node[dep] = set()

            plain_names = self.names(dist.requires())
            if self.extras:
                for extra in dist.extras:
                    for dep in (self.names(dist.requires((extra,)))
                                & ws_names - plain_names):
                        node.setdefault(dep, set()).add(extra)

            self.roots -= set(node)

    def filter(self, collection):
        return set(x for x in collection if not self.ignored(x.project_name))

    def names(self, collection):
        return set(x.project_name for x in self.filter(collection))


class Node(dict):
    """A graph node representing and egg and its dependencies.
    """

    def __init__(self, graph, spec):
        self.name = spec.project_name
        self.graph = graph
        self.requirements = set()
        self.is_dead_end = self.graph.is_dead_end(self.name)
        if isinstance(spec, pkg_resources.Distribution):
            self.req = spec.as_requirement()
        else:
            self.req = spec
        try:
            self.dist = self.graph.working_set.find(self.req)
        except pkg_resources.VersionConflict:
            self.dist = None
