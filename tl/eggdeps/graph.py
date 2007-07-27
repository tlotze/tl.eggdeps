# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

import sys
import pkg_resources


class Graph(dict):
    """A graph of egg dependencies.
    """

    def __init__(self, ignored, is_dead_end):
        self.ignored = ignored
        self.is_dead_end = is_dead_end
        self.roots = ()

    def from_requirements(self, requirement_strings):
        ws = pkg_resources.working_set
        requirements = set(pkg_resources.Requirement.parse(req)
                           for req in requirement_strings)
        self.roots = self.names(requirements)

        for req in requirements:
            self.add_requirement(req)

    def add_requirement(self, req):
        name = req.project_name
        if self.ignored(name):
            return
        if self.is_dead_end(name):
            self[name] = {}
            return

        dist = pkg_resources.get_distribution(req)
        plain_reqs = set(dist.requires())
        extra_reqs = set(dist.requires(req.extras)) - plain_reqs

        plain_names = self.names(plain_reqs)
        if name in self:
            self[name]["extra"].update(self.names(extra_reqs) - plain_names)
        else:
            self[name] = {None: plain_names,
                          "extra": self.names(extra_reqs) - plain_names,
                          }
            for req in plain_reqs:
                self.add_requirement(req)

        for req in extra_reqs:
            self.add_requirement(req)

    def from_working_set(self):
        ws = pkg_resources.working_set
        ws_names = self.names(ws)
        self.roots = ws_names.copy()

        for dist in ws:
            name = dist.project_name
            if self.ignored(name):
                continue

            all_names = self.names(dist.requires(dist.extras))
            self.roots -= all_names

            if self.is_dead_end(name):
                self[name] = {}
                continue

            plain_names = self.names(dist.requires())
            self[name] = {
                None: plain_names.intersection(ws_names),
                "extra": (all_names - plain_names).intersection(ws_names),
                }

    def names(self, collection):
        return set(item.project_name for item in collection
                   if not self.ignored(item.project_name))
