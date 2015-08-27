#!/usr/bin/env python

import sys, argparse
from eos.api.EOS_API import EOS_API

# ===========================================================================
# Command line utility for controlling the EOS lamp
# ===========================================================================

def main():
    # define the parser arguments
    parser = argparse.ArgumentParser(description='Control the EOS lamp')
    parser.add_argument('action', help='the action to take')
    parser.add_argument('arguments', help='the arguments for the specific action', nargs="*")

    args = parser.parse_args()

    # some debug output
    print "EOS interface v1.0"
    print hilite(" * action:    %s" % args.action)
    print hilite(" * arguments: %s" % args.arguments)

    # do a little PARSING
    arguments = map(parse_argument, args.arguments)

    print(arguments)

    # execute the action
    # TODO: pass any optional arguments to the function
    print hilite(" * result:    %s" % EOS_API(args.action, arguments))

### FUNCTIONS
def parse_argument(argument):
    if argument[0] == '#':  # color value
        return int(argument[1:], 16)
    if len(argument) > 1 and argument[0:2] == '0x': # hex value
        return int(argument, 0)
    else:
        return argument

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

if __name__=="__main__":
   main()
