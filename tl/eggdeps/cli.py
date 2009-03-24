# Copyright (c) 2007-2009 Thomas Lotze
# See also LICENSE.txt

import optparse
import re
import sys

import tl.eggdeps.graph
import tl.eggdeps.dot
import tl.eggdeps.requirements
import tl.eggdeps.plaintext


def eggdeps(**defaults):
    parser = optparse.OptionParser("usage: %prog [options] [specifications]")
    parser.add_option("-i", "--ignore",
                      dest="ignore", action="append",
                      default=defaults.get("ignore", []),
                      help="project names to ignore")
    parser.add_option("-I", "--re-ignore",
                      dest="re_ignore", action="append",
                      default=defaults.get("re_ignore", []),
                      help="regular expression for project names to ignore")
    parser.add_option("-e", "--dead-end",
                      dest="dead_ends", action="append",
                      default=defaults.get("dead_ends", []),
                      help="names of projects whose dependencies to ignore")
    parser.add_option("-E", "--re-dead-end",
                      dest="re_dead_ends", action="append",
                      default=defaults.get("re_dead_ends", []),
                      help="regular expression for project names "
                           "whose dependencies to ignore")
    parser.add_option("-x", "--no-extras",
                      dest="extras", action="store_false",
                      default=defaults.get("extras", True),
                      help="always omit extra dependencies")
    parser.add_option("-n", "--version-numbers",
                      dest="version_numbers", action="store_true",
                      default=defaults.get("version_numbers", False),
                      help="print version numbers of active distributions")
    parser.add_option("-1", "--once",
                      dest="once", action="store_true",
                      default=defaults.get("once", False),
                      help="in plain text output, include each distribution "
                           "only once")
    parser.add_option("-t", "--terse",
                      dest="terse", action="store_true",
                      default=defaults.get("terse", False),
                      help="in plain text output, omit any hints at "
                            "unprinted distributions, such as ellipses")
    parser.add_option("-d", "--dot",
                      dest="format", action="store_const",
                      const="dot",
                      default=defaults.get("format", "plaintext"),
                      help="produce a dot graph")
    parser.add_option("-c", "--cluster",
                      dest="cluster", action="store_true",
                      default=defaults.get("cluster", False),
                      help="in a dot graph, cluster direct dependencies "
                           "of each root distribution")
    parser.add_option("-r", "--requirements",
                      dest="format",  action="store_const",
                      const="requirements",
                      help="produce a requirements list")
    parser.add_option("-s", "--version-specs",
                      dest="version_specs", action="store_true",
                      default=defaults.get("version_specs", False),
                      help="in a requirements list, print loosest possible "
                           "version specifications")
    options, specifications = parser.parse_args()

    show = unmatcher(options.ignore, options.re_ignore)
    follow = unmatcher(options.dead_ends, options.re_dead_ends)

    graph = tl.eggdeps.graph.Graph(show=show,
                                   follow=follow,
                                   extras=options.extras,
                                   )

    if specifications:
        graph.from_specifications(*specifications)
    else:
        graph.from_working_set()

    options.comment = 'arguments: ' + ' '.join(sys.argv[1:])
    if defaults:
        options.comment += '\ndefaults:\n' + '\n'.join(
            '%s=%r' % item for item in sorted(defaults.iteritems()))

    formatter = {
        "plaintext": tl.eggdeps.plaintext.print_graph,
        "dot": tl.eggdeps.dot.print_dot,
        "requirements": tl.eggdeps.requirements.print_list,
        }[options.format]
    formatter(graph, options)


def unmatcher(names, patterns):
    names = set(names)
    compiled_patterns = [re.compile(pattern) for pattern in patterns]

    def unmatch(name):
        if name in names:
            return False

        for re in compiled_patterns:
            if re.search(name):
                return False

        return True

    return unmatch
