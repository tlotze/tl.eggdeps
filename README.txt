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

-x, --no-extras       always omit extra dependencies

-n, --version-numbers print version numbers of active distributions

-1, --once            in plain text output, include each distribution only
                      once

-t, --terse           in plain text output, omit any hints at unprinted
                      distributions, such as ellipses

-d, --dot             produce a dot graph

-c, --cluster         in a dot graph, cluster direct dependencies of each
                      root distribution

-r, --requirements    produce a requirements list

-s, --version-specs   in a requirements list, print loosest possible version
                      specifications

The ``-i``, ``-I``, ``-e``, and ``-E`` options may occur multiple times.

If both the ``-d`` and ``-r`` options are given, the one listed last wins.
When printing requirements lists, ``-v`` wins over ``-s``.

The script entry point recognizes default values for all options, the variable
names being the long option names with any dashes replaced by underscores
(except for ``--no-extras``, which translates to setting ``extras=False``).
This allows for setting defaults using the ``arguments`` option of the egg
recipe in a buildout configuration, for example.


Documentation
=============

The goal of ``eggdeps`` is to compute a directed dependency graph with nodes
that represent egg distributions from the working set, and edges which
represent either mandatory or extra dependencies between the eggs.

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

Some information will be lost while building the graph:

- If a dependency occurs both mandatorily and by way of one or more extras, it
  will be recorded as a plain mandatory dependency.

- If a distribution A with installed extras is a dependency of multiple other
  distributions, they will all appear to depend on A with all its required
  extras, even if they individually require none or only a few of them.

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

There are two ways ``eggdeps`` can output the computed dependency graph: plain
text (the default) and a dot file to be fed to the graphviz tools.

Plain text output
~~~~~~~~~~~~~~~~~

The graph is printed to standard output essentially one node per line,
indented according to nesting depth, and annotated where appropriate. The
dependencies of each node are sorted after the following criteria:

- Mandatory dependencies are printed before extra requirements.

- Dependencies of each set of extras are grouped, the groups being sorted
  alphabetically by the names of the extras.

- Dependencies which are either all mandatory or by way of the same set of
  extras are sorted alphabetically by name.

As an illustrating example, the following dependency graph was computed for
two Zope packages, one of them required with a "test" extra depending on an
uninstalled egg, and some graph reduction applied::

  zope.annotation
      zope.app.container *
      zope.component
          zope.deferredimport
              zope.proxy
          zope.deprecation
          zope.event
  zope.dublincore
      zope.annotation ...
    [test]
      (zope.app.testing) *

:Brackets []:
  If one or more dependencies of a node are due to extra requirements only,
  the names of those extras are printed in square brackets above their
  dependencies, half-indented relative to the node which requires them.

:Ellipsis ...:
  If a node with further dependencies occurs at several places in the graph,
  the subgraph is printed only once, the other occurences being marked by an
  ellipsis. The place where the subgraph is printed is chosen such that

  * extra dependencies occur as late as possible in the path, if at all,

  * shallow nesting is preferred,

  * paths early in the alphabet are preferred.

:Parentheses ():
  If a distribution is not in the working set, its name is parenthesised.

:Asterisk *:
  Dead ends are marked by an asterisk.

Dot file output
~~~~~~~~~~~~~~~

In a dot graphics, nodes and edges are not annotated with text but colored.

These are the color codes for nodes, later ones overriding earlier ones in
cases where more than one color is appropriate:

:Green:
  Nodes corresponding to the roots of the graph.

:Yellow:
  Direct dependencies of any root nodes, whether mandatory or through extras.

:Lightgrey:
  Dead ends.

:Red:
  Nodes for eggs installed at a version incompatible with some requirement, or
  not installed at all.

Edge colors:

:Black:
  Mandatory dependencies.

:Lightgrey:
  Extra dependencies.

Other than being highlighted by color, root nodes and their direct
dependencies may be clustered. ``eggdeps`` tries to put each root node in its
own cluster. However, if two or more root nodes share any direct dependencies,
they will share a cluster as well.

Requirements list
~~~~~~~~~~~~~~~~~

All the distributions included in the graph may be output as the Python
representation of a list of requirement specifications, either

- listing bare package names,

- including the exact versions as they occur in the working set, or

- specifying complex version requirements that take into account all version
  requirements made for the distribution in question (but disregard extras
  completely for the time being). Complex version requirements always require
  at least the version that occurs in the working set, assuming that we cannot
  know the version requirements of past versions but reasonably assume that
  requirements might stay the same for future versions.

The list is sorted alphabetically by distribution name.


Change log
==========

For a continuously updated change log, see
<https://svn.thomas-lotze.de/repos/public/tl.eggdeps/trunk/CHANGES.txt>.


Contact
=======

This package is written by Thomas Lotze. Please contact the author at
<thomas@thomas-lotze.de> to provide feedback, suggestions, or contributions.

See also <http://www.thomas-lotze.de/en/software/eggdeps/>.


.. Local Variables:
.. mode: rst
.. End:
