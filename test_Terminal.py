#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/SysLog/test_Terminal.py,

"""
Unit tests for terminal module
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import unittest
from Terminal import TerminalControl

class TestTerminalControl(unittest.TestCase):
    """Unit test class for terminal module"""
    
    def testFontColour(self):
        """Output coloured text"""
        term = TerminalControl()
        if term.colourSupport:
            colours = ["black", "blue", "green","cyan","red","magenta","yellow","white"]
            for colour in colours:
                term.cprintln(" dim "+colour, colour, "dim")
                term.cprintln("bold "+colour, colour, "bold")
        else:
            print "Terminal does not support colour output"
    
    def testCursor(self):
        """Control cursor movement"""
        term = TerminalControl()
        if term.cursorSupport:
            print "Cursor control:"
            term.cprint("ERROR!")
            term.cursor_home()
            print "      "
            term.cprint("ERROR!")
            for i in range(6):
                term.cursor_left()
            print "      "
            print "   S - This should say 'PASS'"
            term.cursor_up()
            print "  S"
            term.cursor_up()
            print " A"
            term.cursor_up()
            print "P"
        else:
            print "Terminal does not support cursor control"

    def testClear(self):
        """Clear areas of the screen"""
        term = TerminalControl()
        if term.cursorSupport:
            print "Screen clearing:"
            term.cprint("ERROR!")
            term.clear_bol()
            term.cprint("ERROR! (Will also fail if cursor control not working)")
            term.cursor_home()
            term.clear_eol()
        else:
            print "Terminal does not support screen clearing"

if __name__ == "__main__":
    print "Visual inspection required to verify correct output"
    unittest.main()

#

#