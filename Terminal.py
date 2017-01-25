#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/SysLog/Terminal.py,

"""
Terminal output control module.
Provides class for implementing basic terminal control and output formatting.

On systems that support ANSI escape sequences, this uses the curses module
On Windows systems this uses the ctypes module to interface with the Windows API. This included with
Python v2.5, or can be downloaded from http://sourceforge.net/projects/ctypes
On Systems that do not support the above, no formatted output is available
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import sys, time
try:
    import ctypes
    class COORD(ctypes.Structure):
        _fields_ = [("x", ctypes.c_short),
                    ("y", ctypes.c_short)]

        def __init__(self, x=0, y=0):
            self.x = x
            self.y = y

    class SMALL_RECT(ctypes.Structure):
        _fields_ = [("Left", ctypes.c_short),
                    ("Top", ctypes.c_short),
                    ("Right", ctypes.c_short),
                    ("Bottom", ctypes.c_short)]

    class SCREEN_INFO(ctypes.Structure):
        _fields_ = [("dwSize", COORD),
                    ("dwCursorPos", COORD),
                    ("wAttributes", ctypes.c_uint),
                    ("srWindow", SMALL_RECT),
                    ("dwMaxWindowSize", COORD)]
except:
    pass

class TerminalControl(object):
    """
    Class to implement control of a terminals output.
    Provides basic cursor control, screen clearing and text colouring.
    """
    def __init__(self):
        """
        Terminal object constructor.
        Configures instance attributes to provide terminal support where available.
        For unsupported terminals, all instance attributes will be empty strings.
        
        @type  term: stream
        @param term: The terminal output stream (currently only stdout is supported)
        """
        self.terminalSupport = False
        self.maxPeriod = 0
        self.colours = {}
        self.commands = {}

        # Check curses module is available and that the terminal is a tty
        self.cursesSupport = False
        self.ctypesSupport = False
        self.colourSupport = False
        self.cursorSupport = False
        try:
            if sys.stdout.isatty():
                import curses
                curses.setupterm()
                self.cursesSupport = True
        except:
            pass

        if not self.cursesSupport:
            try:
                STD_OUTPUT_HANDLE = -11
                self.stdout_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
                self.ctypesSupport = True
                if self.winSetColour(7):
                    self.colourSupport = True
                    self.cursorSupport = True
            except:
                pass

        colours = ["black", "blue", "green","cyan","red","magenta","yellow","white", "normal", "bold", "dim"]

        if self.cursesSupport:
            # Get capabilities, control sequences and colour codes for terminal
            self.termCols = curses.tigetnum('cols')
            self.termRows = curses.tigetnum('lines')

            commands = {"setColour":"setf",
                        "normal":"sgr0",
                        "bold":"bold",
                        "dim":"dim",
                        "cursor_home":"cr",
                        "cursor_up":"cuu1",
                        "cursor_down":"cud1",
                        "cursor_left":"cub1",
                        "cursor_right":"cuf1",
                        "clear_screen":"clear",
                        "clear_eol":"el",
                        "clear_bol":"el1"}

            try:
                if curses.tigetstr(setf):
                    self.colourSupport = True
                if curses.tigetstr(cuu1):
                    self.cursorSupport = True
            except:
                pass

            for command, control_str in commands.items():
                    self.commands[command] = curses.tigetstr(control_str) or ''
            if self.commands["setColour"]:
                self.colourSupport = True
                for index, colour in enumerate(colours):
                    if colour in self.commands:
                        self.colours[colour] = self.commands[colour]
                    else:
                        self.colours[colour] = curses.tparm(self.commands["setColour"], index) or ''
            if self.commands["cursor_up"]:
                self.cursorSupport = True

        elif self.ctypesSupport:
            for index, colour in enumerate(colours):
                self.colours[colour] = index
            self.colours["normal"] = 7
            self.colours["bold"] = 8
            self.colours["dim"] = 0

    def cprint(self, message, *format):
        """
        Outputs given string using specified font colour.
        Does not automatically add CR/LF at end of line

        @type  message: string
        @param message: The text to be output
        @type   format: parameterised list
        @param  format: A list of colour styles to apply to the outputted text
        """
        if self.colourSupport:
            if self.cursesSupport:
                text = ""
                for fmt in format:
                    if fmt in self.colours:
                        text = text + self.colours[fmt]
                message = text + message + self.colours["normal"]
            elif self.ctypesSupport:
                colour = self.colours["normal"]
                if format:
                    colour = 0
                    for fmt in format:
                        if fmt in self.colours:
                            colour = colour + self.colours[fmt]
                self.winSetColour(colour)
        print message,
        if self.ctypesSupport:
            self.winSetColour(self.colours["normal"])
        sys.stdout.softspace = 0

    def cprintln(self, message, *format):
        """
        Outputs given string using specified font colour.
        Forces CR/LF at end of line.

        @type  message: string
        @param message: The text to be output
        @type   format: parameterised list
        @param  format: A list of colour styles to apply to the outputted text
        """
        self.cprint(message, *format)
        print

    def winSetColour(self, colour):
        """
        Sets console font colout using ctypes and Windows API
        
        @type  colour: int
        @param colour: The colour to set for console text output
        @rtype:  boolean
        @return: True if setting console colour was successful, False otherwise
        """
        result = ctypes.windll.kernel32.SetConsoleTextAttribute(self.stdout_handle, colour)
        return result

    def get_screen_info(self):
        INFO_BUFFER = SCREEN_INFO()
        ctypes.windll.kernel32.GetConsoleScreenBufferInfo(self.stdout_handle, ctypes.byref(INFO_BUFFER))
        x = INFO_BUFFER.dwCursorPos.x
        y = INFO_BUFFER.dwCursorPos.y
        max_x = INFO_BUFFER.dwSize.x
        max_y = INFO_BUFFER.dwSize.y
        return (x, y, max_x, max_y)

    def set_cursor_pos(self, x, y):
        """
        Sets the console cursor position using ctypes and Windows API
        
        @type  x: int
        @param x: The column in which to position the cursor
        @type  y: int
        @param y: The row in which to position the cursor
        @rtype:  boolean
        @return: True if setting cursor position was successful, False otherwise
        """
        dwCursorPos = COORD(x, y)
        result = ctypes.windll.kernel32.SetConsoleCursorPosition(self.stdout_handle, dwCursorPos)
        return result

    def cursor_home(self):
        """
        Sets the cursor position to the start of the current row using ctypes and Windows API
        
        @rtype:  boolean
        @return: True if setting cursor position was successful, False otherwise
        """
        if self.cursorSupport:
            if self.cursesSupport:
                self.cprint(self.commands["cursor_home"])
                result = True
            elif self.ctypesSupport:
                x, y, max_x, max_y = self.get_screen_info()
                result = self.set_cursor_pos(0, y)
        else:
            result = False
        return result

    def cursor_up(self):
        """
        Moves the cursor position up one row using ctypes and Windows API
        
        @rtype:  boolean
        @return: True if setting cursor position was successful, False otherwise
        """
        if self.cursorSupport:
            if self.cursesSupport:
                self.cprint(self.commands["cursor_up"])
                result = True
            elif self.ctypesSupport:
                x, y, max_x, max_y = self.get_screen_info()
                if y:
                    y -= 1
                    result = self.set_cursor_pos(x, y)
        else:
            result = False
        return result

    def cursor_down(self):
        """
        Moves the cursor position down one row using ctypes and Windows API
        
        @rtype:  boolean
        @return: True if setting cursor position was successful, False otherwise
        """
        if self.cursorSupport:
            if self.cursesSupport:
                self.cprint(self.commands["cursor_down"])
                result = True
            elif self.ctypesSupport:
                x, y, max_x, max_y = self.get_screen_info()
                if y < max_y:
                    y += 1
                    result = self.set_cursor_pos(x, y)
        else:
            result = False
        return result

    def cursor_left(self):
        """
        Moves the cursor position left one character using ctypes and Windows API
        
        @rtype:  boolean
        @return: True if setting cursor position was successful, False otherwise
        """
        if self.cursorSupport:
            if self.cursesSupport:
                self.cprint(self.commands["cursor_left"])
                result = True
            elif self.ctypesSupport:
                x, y, max_x, max_y = self.get_screen_info()
                if x:
                    x -= 1
                    result = self.set_cursor_pos(x, y)
        else:
            result = False
        return result

    def cursor_right(self):
        """
        Moves the cursor position right one character using ctypes and Windows API
        
        @rtype:  boolean
        @return: True if setting cursor position was successful, False otherwise
        """
        if self.cursorSupport:
            if self.cursesSupport:
                self.cprint(self.commands["cursor_right"])
                result = True
            elif self.ctypesSupport:
                x, y, max_x, max_y = self.get_screen_info()
                if x < max_x:
                    x += 1
                    result = self.set_cursor_pos(x, y)
        else:
            result = False
        return result

    def clear_screen(self):
        """
        Clears the screen using ctypes and Windows API
        
        @rtype:  boolean
        @return: True if setting cursor position was successful, False otherwise
        """
        if self.cursorSupport:
            if self.cursesSupport:
                self.cprint(self.commands["clear_screen"])
                result = True
            elif self.ctypesSupport:
                x, y, max_x, max_y = self.get_screen_info()
                self.cursor_home()
                while y:
                    self.cursor_home()
                    self.clear_eol()
                    self.cursor_up()
                    y -= 1
                x, y, max_x, max_y = self.get_screen_info()
                result = (x == y == 0)
        else:
            result = False
        return result

    def clear_eol(self):
        """
        Clears from the current cursor position to the end of the line using ctypes and Windows API
        
        @rtype:  boolean
        @return: True if setting cursor position was successful, False otherwise
        """
        if self.cursorSupport:
            if self.cursesSupport:
                self.cprint(self.commands["clear_eol"])
                result = True
            elif self.ctypesSupport:
                x, y, max_x, max_y = self.get_screen_info()
                self.cprint(' '*max_x)
                result = self.cursor_up()
        else:
            result = False
        return result

    def clear_bol(self):
        """
        Clears from the current cursor position to the beginning of the line using ctypes and Windows API
        
        @rtype:  boolean
        @return: True if setting cursor position was successful, False otherwise
        """
        if self.cursorSupport:
            if self.cursesSupport:
                self.cprint(self.commands["clear_bol"])
                result = True
            elif self.ctypesSupport:
                x, y, max_x, max_y = self.get_screen_info()
                result = self.cursor_home()
                self.cprint(' '*x)
        else:
            result = False
        return result

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#

#