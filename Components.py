#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Network/Components.py,

"""
Network Terminal Representation Module
Provides a scheme for specifying a radio network.
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

from Enum.eHwType import eHwType
from Enum.eTestStatus import eTestStatus

class SlotInfo(object):
    """
    Details of a particular slot - card type, etc.
    An instance of this object is created for each slot in a terminal.
    """
    #def __init__(self, hwType=eHwType.HW_TYPE_EMPTY, hsc=0, serial="", part="", status=eTestStatus.UNUSED):
    def __init__(self):
        """
        Slot information initialisation.
        """
        self.hwType = eHwType.HW_TYPE_EMPTY
        self.hsc    = 0
        self.serial = ""
        self.part   = ""
        self.status = eTestStatus.UNUSED

class OduInfo(object):
    """
    Details of a particular ODU - type, etc.
    An instance of this object is created for each slot in a terminal.
    """
    def __init__(self):
        """
        ODU information initialisation.
        """
        self.id     = 0
        self.hwType = eHwType.HW_TYPE_EMPTY
        self.hsc    = 0
        self.serial = ""
        self.part   = ""
        self.desc   = ""
        self.status = eTestStatus.UNUSED

class TerminalInfo(object):
    """
    Base class for radio terminal
    Details of a particular terminal - type, address etc.
    """
    def __init__(self):
        """
        Terminal information initialisation.
        """
        self.id      = 0
        self.address = "0.0.0.0"
        self.hwType  = eHwType.HW_TYPE_EMPTY
        self.hsc     = 0
        self.serial  = ""
        self.part    = ""
        self.desc    = ""
        self.status  = eTestStatus.UNUSED

class RadioTerminal(TerminalInfo):
    """
    Combined terminal and slot information.
    """
    def __init__(self):
        """
        Terminal information initialisation.
        """
        TerminalInfo.__init__(self)
        self.slot = {}
        self.odu  = {}
        for i in xrange(1,13):
            self.slot[i] = SlotInfo()
            #self.odu[i] = OduInfo()

class RadioLink(object):
    """
    """
    def __init__(self):
        """
        Link information initialisation.
        """
        self.id     = 0
        self.terminals = []
        self.pointA = []
        self.pointB = []
        self.desc   = ""
        self.status = eTestStatus.UNUSED
        self.protected = 0

class RadioNetwork(object):
    """
    """
    def __init__(self):
        """
        Network information initialisation.
        """
        self.id        = 0
        self.terminals = []
        self.links     = []
        self.status    = eTestStatus.UNUSED

    def addTerminal(self, terminal_id):
        """
        Adds a terminal to the network
        """
        if not terminal_id in self.terminals:
            self.terminals.append(terminal_id)

    def removeTerminal(self, terminal_id):
        """
        Removes a terminal from the network
        """
        for index, terminal in enumerate(self.terminals):
            if terminal == terminal_id:
                self.terminals.pop(index)
                break

    def addLink(self, link_id):
        """
        Adds a link to the network
        """
        if not link_id in self.links:
            self.links.append(link_id)

    def removeLink(self, link_id):
        """
        Removes a link from the network
        """
        for index, link in enumerate(self.links):
            if link == link_id:
                self.links.pop(index)
                break

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

