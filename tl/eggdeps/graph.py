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

    def from_requirements(self, specs):
        requirements = set(pkg_resources.parse_requirements(specs))
        self.roots = self.names(requirements)

        for req in self.filter(requirements):
            self.add_requirement(req)

    def add_requirement(self, req):
        node = self.setdefault(req.project_name, Node(self, req))
        if node.is_dead_end or not node.is_active:
            return

        dist = self.working_set.find(req)
        if not node:
            for dep in self.names(dist.requires()):
                node[dep] = set()

        new_reqs = set(dist.requires())
        if self.extras:
            plain_names = self.names(new_reqs)
            for extra in req.extras:
                extra_reqs = dist.requires((extra,))
                new_reqs.update(extra_reqs)
                for dep in self.names(extra_reqs) - plain_names:
                    node.setdefault(dep, set()).add(extra)

        new_reqs -= node.requirements
        node.requirements.update(new_reqs)
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

            for dep in self.names(dist.requires()).intersection(ws_names):
                node[dep] = set()

            plain_names = self.names(dist.requires())
            if self.extras:
                for extra in dist.extras:
                    for dep in self.names(dist.requires((extra,))).\
                            intersection(ws_names) - plain_names:
                        node.setdefault(dep, set()).add(extra)

            self.roots -= set(node)

    def filter(self, collection):
        return set(x for x in collection if not self.ignored(x.project_name))

    def names(self, collection):
        return set(x.project_name for x in self.filter(collection))


class Node(dict):
    """A graph node representing and egg and its dependencies.
    """

    @property
    def is_dead_end(self):
        return self.graph.is_dead_end(self.name)

    @property
    def is_active(self):
        return bool(self.graph.working_set.find(self.req))

    def __init__(self, graph, spec):
        self.name = spec.project_name
        self.graph = graph
        self.req = pkg_resources.Requirement.parse(self.name)
        self.requirements = set()
