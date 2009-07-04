# Copyright (c) 2007-2009 Thomas Lotze
# See also LICENSE.txt

import pkg_resources


class Graph(dict):
    """A graph of egg dependencies.

    The nodes of the graph represent distributions (sometimes informally
    called 'packages' or 'eggs'). The edges represent dependencies.

    After creating a graph you need to populate it. To collect information
    about all installed packages, call:

        graph = Graph()
        graph.from_working_set()

    To get information about a subset of packages (and their dependencies),
    call:

        graph = Graph()
        graph.from_specifications('package1', 'package2')

    There are options for filtering the graph, described in the docstring of
    the constructor.

    To access a graph node, index the graph using the distribution name as the
    key.

        graph['zope.component']

    Setuptools has this notion of extra dependencies. These are optional and
    are grouped by feature names. For example, 'zope.component' has a 'test'
    extra that pulls in 'zope.testing' and 'zope.location'. Nodes are mappings
    of names of their dependencies to sets of extras by way of which the
    dependencies arise:

        graph['zope.component']['zope.interface'] == set()
        graph['zope.component']['zope.testing'] == set(['test'])

    """

    def __init__(self,
                 working_set=None,
                 show=lambda name: True,
                 follow=lambda name: True,
                 extras=True,
                 ):
        """Create a dependency graph.

        The graph is initially empty. To populate it with nodes and edges call
        either ``from_working_set`` or ``from_specifications``.

        You can specify filtering functions:

          show(name): Returns True if the package with the given name and its
                      dependencies ought to be included in the graph.

          follow(name): Return True if the package with the given name ought
                        to have its dependencies parsed and included in the
                        graph.

        You can also indicate whether you want to process information about
        extra dependencies: if extras is False, all information about extras
        will be discarded.

        """
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
            self._add_requirement(req)

    def _add_requirement(self, req):
        """Add nodes for a distribution and its dependencies.

        This is the recursive part of building the graph from specifications.
        If the distribution can not be found at the required version, a node
        will still be added for it but its dependencies can not be determined.
        """
        node = self.setdefault(req.project_name, Node(self, req))
        if not (node.require(req) and node.follow):
            return

        if not node:
            for dep in self.names(node.dist.requires()):
                node.depend(dep)

        new_reqs = set(node.dist.requires())
        if self.extras:
            plain_names = self.names(new_reqs)
            for extra in req.extras:
                extra_reqs = node.dist.requires((extra,))
                new_reqs.update(extra_reqs)
                for dep in self.names(extra_reqs) - plain_names:
                    node.extra_depend(extra, dep)

        new_reqs -= node._requires
        node._requires |= new_reqs
        for req in filter(self.show_dist, new_reqs):
            self._add_requirement(req)

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
                node.depend(dep)

            if self.extras:
                for extra in dist.extras:
                    for dep in (
                        self.names(filter(self.find, dist.requires((extra,))))
                        - plain_names):
                        node.extra_depend(extra, dep)

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
        self.follow = self.graph.follow(self.name)
        self.require(specification)
        self._requires = set()

    def require(self, specification):
        """Find a matching distribution in the working set.

        Returns whether a distribution compatible with the specification
        (requirement or another distribution) could be found.

        Raises ValueError if the specification is for a different project.
        """
        # Is this for us?
        if specification.project_name != self.name:
            raise ValueError("A %r node cannot satisfy a %r requirement." %
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

    def depend(self, dep):
        """Store a dependency on another distribution.

        dep: name of a dependency

        """
        self[dep] = set()

    def extra_depend(self, extra, dep):
        """Store an extra dependency on another distribution.

        extra: name of an extra via which self depends on dep
        dep: name of a dependency

        """
        if self.get(dep) == set():
            # don't record extra dependencies that duplicate a non-extra one
            return

        self.setdefault(dep, set()).add(extra)

    def iter_deps(self):
        return self.iteritems()

    def iter_deps_by_extras(self):
        return sorted((sorted(extras), dep)
                      for dep, extras in self.iteritems())
