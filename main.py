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
print "the action to take is %s" % args.action
print "with arguments %s" % args.arguments

# execute the action
# TODO: pass any optional arguments to the function
print EOS_API(args.action, args.arguments)