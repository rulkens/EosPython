#!/usr/bin/env python

import sys, argparse
from lib.api.EOS_API import EOS_API

# ===========================================================================
# Command line utility for controlling the EOS lamp
# ===========================================================================

# define the parser arguments
parser = argparse.ArgumentParser(description='Control the EOS lamp')
parser.add_argument('action', help='the action to take')
parser.add_argument('arguments', help='the arguments for the specific action', nargs="*")

args = parser.parse_args()

# utility functions
def hilite(string, status=True, bold=False):
    attr = []
    if status:
        # green
        attr.append('32')
    else:
        # red
        attr.append('31')
    if bold:
        attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

# some debug output
print "EOS interface v1.0"
print hilite(" * action:    %s" % args.action)
print hilite(" * arguments: %s" % args.arguments)

# execute the action
# TODO: pass any optional arguments to the function
print hilite(" * result:    %s" % EOS_API(args.action, args.arguments))