#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Traffic/TribTraffic.py,

"""
Interface to tributary traffic functions
Traffic checking available for all terminals that have defined BER tester connections.
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

from BerManager import BerManager
from Snmp import SnmpManager
from Modules import Timer
import time

class TribTraffic(object):
    """
    """
    def __init__(self):
        """
        """
        #self.stats = {}
        #self.stats["ErrorCount"] = 0
        self._manager = BerManager()
        mgr = SnmpManager.SnmpManager()
        self._context = "terminal"
        self._terminalId = 0

    def _getDacContext(self, slot=0, trib=0):
        if self._context == "terminal":
            #use ber connection information to decide trib
            pass
        if self._context.startswith("slot"):
            #use ber connection information to decide trib
            pass
        if slot:
            
            pass
        if trib:
            pass
        return (slot, trib)

    def start(self, terminal, slot, trib):
        self._manager.ber_function("start", terminal, slot, trib)

    def stop(self, terminal, slot, trib):
        self._manager.ber_function("stop", terminal, slot, trib)

    def set_type(self, terminal, slot, trib, traffic_type):
        """
        Sets the traffic type for the specified terminal, slot and tributary.
        
        @type    terminal: session
        @param   terminal: The terminal
        @type  slot: int
        @param slot: The slot
        @type  trib: int
        @param trib: The trib
        @rtype:  int
        @return: Zero if the requested operation was successful. Non-zero otherwise.
        """
        result = self._manager.ber_function("set_type", terminal, slot, trib, traffic_type)
        result = self._manager.ber_function("reset", terminal, slot, trib)
        if result < 0:
            result = 0
        return result


    def reset(self, terminal, slot, trib):
        """
        Resets traffic generation for the specified terminal, slot and tributary.
        
        @type    terminal: session
        @param   terminal: The terminal
        @type  slot: int
        @param slot: The slot
        @type  trib: int
        @param trib: The trib
        @rtype:  int
        @return: Zero if the requested operation was successful. Non-zero otherwise.
        """
        result = self._manager.ber_function("reset", terminal, slot, trib)
        return result


    def on(self, terminal, slot, trib):
        """
        Enables traffic generation INTO the specified terminal, slot and tributary.
        
        @type    terminal: session
        @param   terminal: The terminal
        @type  slot: int
        @param slot: The slot
        @type  trib: int
        @param trib: The trib
        @rtype:  int
        @return: Zero if the requested operation was successful. Non-zero otherwise.
        """
        result = self._manager.ber_function("on", terminal, slot, trib)
        if result < 0:
            result = 0
        return result


    def off(self, terminal, slot, trib):
        """
        Disables traffic generation INTO the specified terminal, slot and tributary.
        
        @type    terminal: session
        @param   terminal: The terminal
        @type  slot: int
        @param slot: The slot
        @type  trib: int
        @param trib: The trib
        @rtype:  int
        @return: Zero if the requested operation was successful. Non-zero otherwise.
        """
        result = self._manager.ber_function("off", terminal, slot, trib)
        if result < 0:
            result = 0
        return result

    def los_on(self, terminal, slot, trib):
        """
        Disables the channel connected to the terminal specified causing LOS to be
        generated
        
        @type    terminal: session
        @param   terminal: The terminal
        @type  slot: int
        @param slot: The slot
        @type  trib: int
        @param trib: The trib
        @rtype:  int
        @return: Zero if the requested operation was successful. Non-zero otherwise.
        """
        result = self._manager.ber_function("los_on", terminal, slot, trib)
        if result < 0:
            result = 0
        return result


    def los_off(self, terminal, slot, trib):
        """
        Enable the channel connected to the terminal specified
        
        @type    terminal: session
        @param   terminal: The terminal
        @type  slot: int
        @param slot: The slot
        @type  trib: int
        @param trib: The trib
        @rtype:  int
        @return: Zero if the requested operation was successful. Non-zero otherwise.
        """
        result = self._manager.ber_function("los_off", terminal, slot, trib)
        if result < 0:
            result = 0
        return result
    

    def ais_on(self, terminal, slot, trib):
        """
        Enables AIS generation INTO the specified terminal, slot and tributary.
        
        @type    terminal: session
        @param   terminal: The terminal
        @type  slot: int
        @param slot: The slot
        @type  trib: int
        @param trib: The trib
        @rtype:  int
        @return: Zero if the requested operation was successful. Non-zero otherwise.
        """
        result = self._manager.ber_function("ais_on", terminal, slot, trib)
        if result < 0:
            result = 0
        return result


    def ais_off(self, terminal, slot, trib):
        """
        Disables AIS generation INTO the specified terminal, slot and tributary.
        
        @type    terminal: session
        @param   terminal: The terminal
        @type  slot: int
        @param slot: The slot
        @type  trib: int
        @param trib: The trib
        @rtype:  int
        @return: Zero if the requested operation was successful. Non-zero otherwise.
        """
        result = self._manager.ber_function("ais_off", terminal, slot, trib)
        if result < 0:
            result = 0
        return result


    def errors(self, terminal, slot, trib):
        """
        Returns the number of errors for the specified terminal, slot and tributary.
        
        @type    terminal: session
        @param   terminal: The terminal
        @type  slot: int
        @param slot: The slot
        @type  trib: int
        @param trib: The trib
        @rtype:  int
        @return: Zero if the requested operation was successful. Non-zero otherwise.
                 Stats dictionary updated. ErrorCount entry reports number of detected errors.
        """
        result = self._manager.ber_function("check", terminal, slot, trib)
        #result = self.traffic_on(terminal, slot, trib)
        #self.traffic_errors(terminal, slot, trib)
        #self.stats["ErrorCount"] = result
        return result


    def check(self, terminal, slot, trib, duration=10):
        """
        Checks that traffic remains error-free for a duration.
        
        @type  terminal: session
        @param terminal: The terminal
        @type      slot: int
        @param     slot: The slot
        @type      trib: int
        @param     trib: The trib
        @type  duration: int
        @param duration: The duration in seconds to verify traffic for.
        @rtype:  int
        @return: Zero if the traffic was error-free. Number of detected errors otherwise.
                 Stats dictionary updated. ErrorCount entry reports number of detected errors.
        """
        self.reset(terminal, slot, trib)
        Timer.Wait("Checking traffic: "+terminal, duration)
        result = self.errors(terminal, slot, trib)
        return result
        
    def check_poll(self, terminal, slot, trib, retry=1, duration=10):
        while retry > 0:
            self.reset(terminal, slot, trib)
            Timer.Wait("Checking traffic: "+terminal, duration)
            result = self.errors(terminal, slot, trib)
            
            if result == 0:
                break
            
            retry -= 1
            
        return result

    def check_ais(self, terminal, slot, trib, duration=5):
        """
        Checks for AIS for a duration.
        
        @type  terminal: session
        @param terminal: The terminal
        @type      slot: int
        @param     slot: The slot
        @type      trib: int
        @param     trib: The trib
        @type  duration: int
        @param duration: The duration in seconds to verify AIS for.
        @rtype:  int
        @return: Zero if AIS is not active, -1 otherwise
        """
        self.reset(terminal, slot, trib)
        Timer.Wait("Checking for AIS: "+terminal, duration)
        return self._manager.ber_function("check_ais", terminal, slot, trib)

    def check_los(self, terminal, slot, trib, duration=5):
        """
        Checks for LOS for a duration.
        
        @type  terminal: session
        @param terminal: The terminal
        @type      slot: int
        @param     slot: The slot
        @type      trib: int
        @param     trib: The trib
        @type  duration: int
        @param duration: The duration in seconds to verify LOS for.
        @rtype:  int
        @return: Zero if AIS is not active, -1 otherwise
        """
        self.reset(terminal, slot, trib)
        Timer.Wait("Checking for LOS: "+terminal, duration)
        return self._manager.ber_function("check_los", terminal, slot, trib)

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#
