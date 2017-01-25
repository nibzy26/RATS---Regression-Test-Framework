#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Traffic/BerTester.py

"""
Base class for BER testers.
Provides interface to BER tester functions for traffic control and checking.
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

from eBerType import eBerType
from Enum.eTribType import eTribType

class BerException(Exception):
    """Base class for BER tester exceptions"""
    pass

class BerNotSupportedError(BerException):
    """Method not supported by ber tester."""
    pass

class BerNotAvailableError(BerException):
    """BER Tester not available for specified terminal/slot/trib."""
    pass

class BerFailError(BerException):
    """BER Tester configuration failed."""
    pass



class BerNode(object):
    """
    Information for a traffic connection node.
    Holds location of terminal, slot and tributary number.
    """
    def __init__(self, ip="", slot=0, trib=0):
        """
        Node initialisation. Set attributes to specified values.
        """
        self.ip = ip
        self.slot = slot
        self.trib = trib


class BerConnection(object):
    """
    Stores information on a connection between a terminal and a BER tester.
    """
    def __init__(self, ip="", slot=0, trib=0, channel=0):
        """
        BER Connection initialisation.
        """
        self.trib_type = eTribType.TRIB_TYPE_UNKNOWN
        self.channel = channel
        self.node = BerNode(ip, slot, trib)
        self.aisCount = 0
        self.losCount = 0
        self.stats = {}

        
class BerTester(object):
    """
    Base class for BER Tester.
    """
    def __init__(self, id=""):
        """
        BER tester initialisation.
        """
        self.id = id
        self.berType = eBerType.BER_TYPE_UNKNOWN
        self.stats = {}
        self.connections = []

    def start(self, *args):
        pass

    def stop(self, *args):
        pass

    def add_connection(self, ip, slot, trib, channel):
        """
        Add a BER connection record to the list.
        Used to register a connection between a BER tester and a terminal.

        @type       ip: string
        @param      ip: IP address of the terminal
        @type     slot: int
        @param    slot: Slot number of the DAC
        @type     trib: int
        @param    trib: Tributary number of the DAC
        @type  channel: int
        @param channel: BER tester channel
        @rtype:  boolean
        @return: True if connection entry was successsfully added.
                 False otherwise.
        """
        #Check if specified node is already assigned to a ber tester
        #conflict = getBer(ip, slot, trib)
        #if conflict:
        #    print ip, " Slot:", slot, " Trib:",
        #    print trib, " already assigned to a Ber tester"
        #    raise
        result = True
        for connection in self.connections:
            if connection.channel == channel:
                print "Ber channel", channel, "already assigned to ", connection.node.ip,
                print " Slot:", connection.node.slot, " Trib:", connection.node.trib
                result = False
        connection = BerConnection(ip, slot, trib, channel)
        self.connections.append(connection)
        return result

    def remove_connection(self, ip="", slot=0, trib=0, channel=0):
        """
        Remove a BER connection record from the list.
        Used to delete a previously defined BER connection.

        @type       ip: string
        @param      ip: IP address of the terminal
        @type     slot: int
        @param    slot: Slot number of the DAC
        @type     trib: int
        @param    trib: Tributary number of the DAC
        @type  channel: int
        @param channel: BER tester channel
        @rtype:  boolean
        @return: True if connection entry was successsfully removed.
                 False otherwise.
        """
        result = False
        for i, connection in enumerate(self.connections):
            if channel:
                if connection.channel == channel:
                    self.connections.pop(i)
                    result = True
                    break
            elif connection.node.ip == ip:
                if connection.node.slot == slot:
                    if connection.node.trib == trib:
                        self.connections.pop(i)
                        result = True
                        break
        return result
    
    def get_connection(self, ip="", slot=0, trib=0, channel=0):
        """
        Find and return a BER connection entry from the list.
        Returns None if no matching connection is found.

        @type       ip: string
        @param      ip: IP address of the terminal
        @type     slot: int
        @param    slot: Slot number of the DAC
        @type     trib: int
        @param    trib: Tributary number of the DAC
        @type  channel: int
        @param channel: BER tester channel
        @rtype:  connection object
        @return: connection object if a matching entry is found.
                 Exception raised if no matching BER connection entry was found.
        """
        #Loop through all connections for the current BER tester
        for connection in self.connections:
            if connection.node.ip == ip:
                if connection.node.slot == slot:
                    if connection.node.trib == trib:
                        #Matching connection found
                        return connection
        #No matching connection found
        return None


    #Default BER tester methods - All raise an exception to indicate that the method is not supported by
    #the BER tester. Individual BER modules should override the methods from this base class as required.


    def set_type(self, *args):
        """
        Sets the traffic type for the specified trib

        @type  args: list
        @param args: Method arguments, which may vary depending on ber tester type
        """
        raise BerNotSupportedError


    def reset(self, *args):
        """
        Activates the PRBS on the specified trib, and resets the error count

        @type  args: list
        @param args: Method arguments, which may vary depending on ber tester type
        """
        raise BerNotSupportedError


    def on(self, *args):
        """
        Activates the PRBS on the specified trib

        @type  args: list
        @param args: Method arguments, which may vary depending on ber tester type
        """
        raise BerNotSupportedError


    def off(self, *args):
        """
        Deactivates the PRBS on the specified trib

        @type  args: list
        @param args: Method arguments, which may vary depending on ber tester type
        """
        raise BerNotSupportedError


    def check(self, *args):
        """
        Returns the error count for the specified trib

        @type  args: list
        @param args: Method arguments, which may vary depending on ber tester type
        """
        raise BerNotSupportedError


    def ais_on(self, *args):
        """
        Enables AIS generation for the specified trib

        @type  args: list
        @param args: Method arguments, which may vary depending on ber tester type
        """
        raise BerNotSupportedError


    def ais_off(self, *args):
        """
        Disables AIS generation on the specified trib

        @type  args: list
        @param args: Method arguments, which may vary depending on ber tester type
        """
        raise BerNotSupportedError

    def los_on(self, *args):
        """
        Enables LOS generation for the specified trib

        @type  args: list
        @param args: Method arguments, which may vary depending on ber tester type
        """
        raise BerNotSupportedError


    def los_off(self, *args):
        """
        Disables LOS generation on the specified trib

        @type  args: list
        @param args: Method arguments, which may vary depending on ber tester type
        """
        raise BerNotSupportedError    



if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#

#
