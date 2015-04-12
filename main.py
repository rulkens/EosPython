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

# some debug output
print "EOS interface v1.0"
print " * action:    %s" % args.action
print " * arguments: %s" % args.arguments

# execute the action
# TODO: pass any optional arguments to the function
print " * result:    %s" % EOS_API(args.action, args.arguments)