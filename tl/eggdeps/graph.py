# Copyright (c) 2007-2009 Thomas Lotze
# See also LICENSE.txt

import pkg_resources


class Graph(dict):
    """A graph of egg dependencies.
    """

    def __init__(self,
                 working_set=None,
                 show=lambda name: True,
                 follow=lambda name: True,
                 extras=True,
                 ):
        self.working_set = working_set or pkg_resources.WorkingSet()
        self.show = show
        self.follow = follow
        self.extras = extras
        self.roots = ()
        self.show_dist = lambda spec: show(spec.project_name)

    def from_specifications(self, *specifications):
        """Build the dependency graph starting from one or more eggs.
        """
        requirements = set(pkg_resources.parse_requirements(specifications))
        self.roots = self.names(requirements)

        for req in filter(self.show_dist, requirements):
            self.add_requirement(req)

    def add_requirement(self, req):
        """Add nodes for a distribution and its dependencies.

        This is the recursive part of building the graph from specifications.
        If the distribution can not be found at the required version, a node
        will still be added for it but its dependencies can not be determined.
        """
        node = self.setdefault(req.project_name, Node(self, req))
        if not (node.find(req) and node.follow):
            return

        if not node:
            for dep in self.names(node.dist.requires()):
                node[dep] = set()

        new_reqs = set(node.dist.requires())
        if self.extras:
            plain_names = self.names(new_reqs)
            for extra in req.extras:
                extra_reqs = node.dist.requires((extra,))
                new_reqs.update(extra_reqs)
                for dep in self.names(extra_reqs) - plain_names:
                    node.setdefault(dep, set()).add(extra)

        new_reqs -= node.requires
        node.requires |= new_reqs
        for req in filter(self.show_dist, new_reqs):
            self.add_requirement(req)

    def from_working_set(self):
        """Build the dependency graph for the whole working set.
        """
        ws = filter(self.show_dist, self.working_set)

        # Construct nodes and dependencies, ignoring any incompatibilities.
        for dist in ws:
            node = self[dist.project_name] = Node(self, dist)
            if not node.follow:
                continue

            plain_names = self.names(filter(self.find, dist.requires()))
            for dep in plain_names:
                node[dep] = set()

            if self.extras:
                for extra in dist.extras:
                    for dep in (
                        self.names(filter(self.find, dist.requires((extra,))))
                        - plain_names):
                        node.setdefault(dep, set()).add(extra)

        # Find roots, including one representative of each root cycle, by
        # removing all direct and implied dependencies of each node from the
        # set of root candidates.
        self.roots = self.names(ws).copy()

        # Consider candidates in alphabetic order for predictability.
        for candidate in sorted(self.roots):
            # When hitting a root cycle, all of its constituents except the
            # candidate being considered will be discarded. To prevent that
            # representative of the cycle from being discarded as a dependency
            # of each of the other cycle constituents, skip considering
            # dependencies of candidates that have already been discarded.
            if candidate not in self.roots:
                continue

            # Walking the candidate's dependencies needs to discard the
            # candidate temporarily in order to break infinite loops.
            self._walk(candidate)
            self.roots.add(candidate)

    def _walk(self, name):
        self.roots.remove(name)
        for dep in self[name]:
            if dep in self.roots:
                self._walk(dep)

    def names(self, specifications):
        """Return a set of project names to be processed from an iterable of
        either requirements or distributions.
        """
        return set(filter(self.show,
                          (x.project_name for x in specifications)))

    def find(self, requirement):
        """Find a distribution in the working set associated with the graph.

        This is a convenience method to handle the VersionConflict exception.
        """
        try:
            return self.working_set.find(requirement)
        except pkg_resources.VersionConflict:
            return None


class Node(dict):
    """A graph node representing an egg and its dependencies.
    """

    dist = None
    compatible = True

    def __init__(self, graph, specification):
        self.name = specification.project_name
        self.graph = graph
        self.requires = set()
        self.follow = self.graph.follow(self.name)
        self.deps = {}
        self.find(specification)

    def find(self, specification):
        """Find a matching distribution in the working set.

        Returns whether a distribution compatible with the specification
        (requirement or another distribution) could be found.

        Raises ValueError if the specification is for a different project.
        """
        # Is this for us?
        if specification.project_name != self.name:
            raise ValueError("A '%s' node cannot find a '%s' distribution." %
                             (self.name, specification.project_name))

        # Search even if the specification is already a distribution to make
        # sure it's active.
        if isinstance(specification, pkg_resources.Distribution):
            specification = specification.as_requirement()
        dist = self.graph.find(specification)

        # Store the distribution if it is found - there can be only one under
        # the same project name in the same working set.
        self.dist = self.dist or dist

        # Remember if at least one requirement could not be met.
        found = bool(dist)
        self.compatible &= found

        return found
