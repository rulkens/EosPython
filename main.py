#!/usr/bin/python

import sys, argparse
from lib.Eos_Driver import EOS_Driver

# ===========================================================================
# Command line utility for controlling the EOS lamp
# ===========================================================================

# create the Eos_Driver object
eos = EOS_Driver()

# functions
def allOff():
    eos.allOff()
def allOn():
    eos.allOn()
def one(opts):
    eos.one(int(opts[0]), float(opts[1]))
def set(opts):
    # convert opts to a list of floats
    eos.set(map(lambda o: float(o), opts))
def all(opts):
    eos.all(float(opts[0]))
def only(opts):
    eos.only(int(opts[0]), float(opts[1]))
def on(opts=None):
    if opts != None and opts != []:
        eos.on(int(opts[0]))
    else:
        eos.allOn()
def off(opts=None):
    if opts != None and opts != []:
        eos.off(int(opts[0]))
    else:
        eos.allOff()
def setFreq(opts):
    eos.setFreq(int(opts[0]))
    
# overview of all the actions possible
actions = {
    'alloff':       allOff,
    'allon':        allOn,
    'one':          one,
    'set':          set,
    'all':          all,
    'only':         only,
    'on':           on,
    'off':          off,
    'setfreq':      setFreq
}



# define the parser arguments
parser = argparse.ArgumentParser(description='Control the EOS lamp')
parser.add_argument('action', help='the action to take')
parser.add_argument('arguments', help='the arguments for the specific action', nargs="*")

args = parser.parse_args()

# some debug output
print "the action to take is %s" % args.action
print "with arguments %s" % args.arguments

def errorHandler():
    print "the action cannot be found"

# execute the action
# TODO: pass any optional arguments to the function
actions.get(args.action, errorHandler)(args.arguments)