#!/usr/bin/env python
# $Header

"""
This module provides multi-level debugging output.


To use debugging output:  from System import debug - import at module, NOT class/method level
To turn ON debug output:  debug.on([level])        - usually inserted directly after module imports
                                                     level specifies the debug output level
To turn OFF debug output: debug.off()              - (default state)
To output debug message:
          debug.out(text, [level, colour, format]) - where text is the string to display
                                                   - level id the debug output level. The message will only
                                                     be shown if this is >= the level specified by debug.on()
                                                   - format may be either "dim" or "bold", default is "dim"
                                                   - colour may be one of those listed below, default is "white"
                                                     "black", "blue", "green","cyan","red","magenta","yellow","white"
"""

__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import types, os.path
from sys import exc_info
from SysLog import Terminal

_debug_modules = {} #List of modules that debug output is turned on for

_debug_terminal = Terminal.TerminalControl()

def _who_called_me(n=1):
    try:
        raise None
    except:
        f = exc_info()[2].tb_frame.f_back.f_back
        fileName     = os.path.split(f.f_code.co_filename)[-1]
        lineNumber   = str(f.f_lineno)
        return fileName, lineNumber

def on(level=0):
    fileName, lineNumber = _who_called_me()
    _debug_modules[fileName] = level
    out(fileName + " Debug ON (Level " + str(level) + ")")

def off():
    fileName, lineNumber = _who_called_me()
    if fileName in _debug_modules:
        del _debug_modules[fileName]
        out(fileName + " Debug OFF")

def out(text="", *args):
    fileName, lineNumber = _who_called_me()
    if fileName in _debug_modules:
        level = 0
        for entry in args:
            if type(entry) == types.IntType:
                level = entry
                args.remove(entry)
        if _debug_modules[fileName] >= level:
            debug_info = "["+fileName+" line "+lineNumber+"] "
            message = debug_info+ " "*(31-len(debug_info)) + text
            _debug_terminal.cprintln(message, *args)

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#
# $Log
#
