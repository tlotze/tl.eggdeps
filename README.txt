==========
tl.eggdeps
==========

The ``eggdeps`` tool reports dependencies between eggs in the working set.
Dependencies are considered recursively, creating a directed graph. This graph
is printed to standard output either as plain text, or as an input file to the
graphviz tools.


Usage
=====

``eggdeps [options] [specifications]``

Specifications must follow the usual syntax for specifying distributions of
Python packages as defined by ``pkg_resources``.

- If any specifications are given, the corresponding distributions will make
  up the roots of the dependency graph, and the graph will be restricted to
  their dependencies.

- If no specifications are given, the graph will map the possible dependencies
  between all eggs in the working set and its roots will be those
  distributions that aren't dependencies of any other distributions.

Options
-------

-h, --help            show this help message and exit

-i IGNORE, --ignore=IGNORE
                      project names to ignore

-I RE_IGNORE, --re-ignore=RE_IGNORE
                      regular expression for project names to ignore

-e DEAD_ENDS, --dead-end=DEAD_ENDS
                      names of projects whose dependencies to ignore

-E RE_DEAD_ENDS, --re-dead-end=RE_DEAD_ENDS
                      regular expression for project names whose
                      dependencies to ignore

-n, --no-extras       always omit extra dependencies

-d, --dot             produce a dot graph

-c, --cluster         in a dot graph, cluster direct dependencies of each
                      root distribution

The ``-i``, ``-I``, ``-e``, and ``-E`` options may occur multiple times.


Documentation
=============

Working set
-----------

The working set ``eggdeps`` operates on is defined by the egg distributions
available to the running Python interpreter. For example, these may be the
distributions activated by ``easy_install`` or installed in a ``zc.buildout``
environment.

If the graph is to be calculated to such specifications that not all required
distributions are in the working set, the missing ones will be marked in the
output, and their dependencies cannot be determined. The same happens if any
distribution that is either specified on the command line or required by any
other distribution is available in the working set, but at a version
incompatible with the specified requirement.

Graph building strategies
-------------------------

The dependency graph may be built following either of two strategies:

:Analysing the whole working set:
  Nodes correspond exactly to the distributions in the working set. Edges
  corresponding to all conceivable dependencies between any active
  distributions are included, but only if the required distribution is active
  at the correct version. The roots of the graph correspond to those
  distributions no other active distributions depend upon.

:Starting from one or more eggs:
  Nodes include all packages depended upon by the specified distributions and
  extras, as well as their deep dependencies. They may cover only part of the
  working set, as well as include nodes for distributions that are not active
  at the required versions or not active at all (so their dependencies can not
  be followed). The roots of the graph correspond to the specified
  distributions.

Reducing the graph
------------------

In order to reduce an otherwise big and tangled dependency graph, certain
nodes and edges may be omitted.

:Ignored nodes:
  Nodes may be ignored completely by exact name or regular expression
  matching. This is useful if a very basic distribution is a depedency of a
  lot of others. An example might be ``setuptools``.

:Dead ends:
  Distributions may be declared dead ends by exact name or regular expression
  matching. Dead ends are included in the graph but their own dependencies
  will be ignored. This allows for large subsystems of distributions to be
  blotted out except for their "entry points". As an example, one might
  declare ``zope.app.*`` dead ends in the context of ``zope.*`` packages.

:No extras:
  Reporting and following extra dependencies may be switched off completely.
  This will probably make most sense when analysing the working set rather
  than the dependencies of specified distributions.

Output
------

In all cases, the output of ``eggdeps`` is a directed dependency graph with
nodes that represent egg distributions and edges which represent either direct
or extra dependencies between them. Some information will be lost while
building the graph:

- If a dependency occurs both directly and by way of one or more extras, it
  will be recorded as a plain direct dependency.

- If a distribution A with installed extras is a dependency of multiple other
  distributions, they will all appear to depend on A with all its extras, even
  if they individually require none or only a few of them.


Contact
=======

This package is written by Thomas Lotze. Please contact the author at
<thomas@thomas-lotze.de> to provide feedback, suggestions, or contributions.

See also <http://www.thomas-lotze.de/en/software/eggdeps/>.
