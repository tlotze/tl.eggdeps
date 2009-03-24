# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

import pprint

import pkg_resources


def print_list(graph, options):
    """Print a requirements list to standard output.

    graph: a tl.eggdeps.graph.Graph instance

    options: an object that provides formatting options as attributes

        version_numbers: bool, print version numbers of active distributions?
    """
    reqs = []
    for name, node in sorted(graph.iteritems()):
        if options.version_numbers:
            reqs.append(node.dist.as_requirement())
        elif options.version_specs:
            reqs.append(common_requirement(graph.working_set, node.dist))
        else:
            reqs.append(pkg_resources.Requirement.parse(name))

    pprint.pprint([str(req) for req in reqs])


def common_requirement(working_set, distribution):
    """Determine common requirement for a distribution made by a working set.

    working_set: iterable of distributions

    dist: distribution

    Returns a requirement for a given distribution that is the largest common
    subset of all requirements made for that distribution by the given working
    set. I.e., its version specification is the intersection of all individual
    version specifications.
    """
    name = distribution.project_name

    # Extract from the working set requirements that apply to the named
    # distribution and specify any version restrictions at all.
    reqs = []
    # XXX take extras into account
    for dist in working_set:
        reqs.extend(req for req in dist.requires() 
                    if req.project_name == name and req.specs)

    inclusions = set((distribution.parsed_version,))
    exclusions = set()
    intervals = [(distribution.parsed_version, None)]
    version_reprs = {distribution.parsed_version: distribution.version}

    for req in reqs:
        r_inclusions = set()
        r_exclusions = set()
        r_intervals = []

        # Normalize requirement, extracting inclusions, exclusions and
        # non-overlapping open intervals.
        lower = None
        upper = None
        for op, version_repr in req.specs:
            version = pkg_resources.parse_version(version_repr)
            version_reprs[version] = version_repr
            if op == "!=":
                r_exclusions.add(version)
                continue
            if "=" in op:
                r_inclusions.add(version)
            if "<" in op:
                upper = version
            elif ">" in op:
                if upper is not None:
                    r_intervals.append((lower, upper))
                    lower = upper = None
                if lower is None:
                    lower = version
        else:
            if lower is not None or upper is not None:
                r_intervals.append((lower, upper))

        # Keep only those common inclusions included in the requirement.
        inclusions.difference_update(r_exclusions)
        for version in inclusions.copy():
            for lower, upper in r_intervals:
                if lower < version and (upper is None or version < upper):
                    break
            else:
                if version not in r_inclusions:
                    inclusions.remove(version)

        # Keep only intersection of interval sets.
        new_intervals = []
        for interval in intervals:
            new_intervals.extend(filter(None, (
                interval_intersection(interval, r_interval)
                for r_interval in r_intervals)))
        intervals = new_intervals

        # Collect exclusions, keep only those inside one of the remaining
        # intervals.
        new_exclusions = set()
        for version in exclusions.union(r_exclusions):
            for lower, upper in intervals:
                if lower < version and (upper is None or version < upper):
                    new_exclusions.add(version)
                    break
        exclusions = new_exclusions

    specs = set((version, "!=") for version in exclusions)
    for lower, upper in intervals:
        if lower in inclusions:
            inclusions.remove(lower)
            specs.add((lower, ">="))
        elif lower is not None:
            specs.add((lower, ">"))
        if upper in inclusions:
            inclusions.remove(upper)
            specs.add((upper, "<="))
        elif upper is not None:
            specs.add((upper, "<"))
    specs.update((version, "==") for version in inclusions)

    intersection = pkg_resources.Requirement.parse(
        name + ",".join((op + version_reprs[version])#
                        for version, op in sorted(specs)))

    return intersection


def interval_intersection((lower1, upper1), (lower2, upper2)):
    """Compute the intersection of two open intervals.

    Intervals are pairs of comparable values, one or both may be None to
    denote (negative) infinity.

    Returns the intersection if it is not empty.

    >>> interval_intersection((1, 3), (2, 4))
    (2, 3)

    >>> interval_intersection((1, 2), (2, 3))

    >>> interval_intersection((None, 1), (None, 2))
    (None, 1)

    >>> interval_intersection((1, None), (2, None))
    (2, None)

    >>> interval_intersection((None, None), (None, None))
    (None, None)

    >>> interval_intersection((None, 1), (1, None))
    """
    lower = max(lower1, lower2)
    if upper1 is None or upper2 is None:
        upper = max(upper1, upper2)
    else:
        upper = min(upper1, upper2)
    if lower < upper or upper is None:
        return lower, upper
