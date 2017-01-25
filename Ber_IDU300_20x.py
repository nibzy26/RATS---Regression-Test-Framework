#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Traffic/Ber_IDU300_20x.py,

"""
Interface to BER tester functions using an IDU 300 20x v1
IDU must be configured for use as a BER tester.
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

from Snmp import SnmpManager
from eBerType import eBerType
from Enum.eTribType import eTribType
from System import ThreadLock
import BerTester

class Ber_IDU300_20x(BerTester.BerTester):
    """
    """
    def __init__(self, id, berAddress, slot):
        """
        """
        self.lock = ThreadLock.LockManager()
        BerTester.BerTester.__init__(self)
        self.berType = eBerType.BER_TYPE_IDU_300_20X
        self.tribType = eTribType.TRIB_TYPE_UNKNOWN
        self.id = id
        self.ip = berAddress
        self.slot = slot
        _manager = SnmpManager.SnmpManager()
        self.berSession =_manager.create_session(self.ip,'terminal')
        for trib in xrange(1,21):
            self.berSession.slot[2].set('tribConfigCommissioned', trib, 1)


    def start(self, ip, slot, trib):
        lockName = "BER Tester " + str(self.id)
        self.lock.lock(lockName)
        self.reset(ip, slot, trib)

    def stop(self, ip, slot, trib):
        lockName = "BER Tester " + str(self.id)
        self.off(ip, slot, trib)
        self.lock.unlock(lockName)
        
    def set_type(self, ip, slot, trib, trafficType):
        """
        Sets the traffic type for the specified trib
        """
        connection = self.get_connection(ip, slot, trib)
        
        #print trafficType, 'E1=', eTribType.TRIB_TYPE_E1 , 'DS1=', eTribType.TRIB_TYPE_DS1
        
        #Check that the specified traffic type is supported
        if (trafficType != eTribType.TRIB_TYPE_E1) and \
            (trafficType != eTribType.TRIB_TYPE_DS1):
            print 'not supported'
            connection.trib_type = eTribType.TRIB_TYPE_UNKNOWN
            raise BerTester.BerNotSupportedError
                
        #Set the BER tester backplane traffic type
        if self.tribType != trafficType:
            self.tribType = trafficType
            try:
                result = self.berSession.terminal.set('ctuUnitConfigCircuitType', 0, trafficType)
            except:
                pass
            if result != trafficType:
                raise BerTester.BerFailError

        #Set the tributary traffic type
        if connection.trib_type != trafficType:
            connection.trib_type = trafficType
            try:
                result = self.berSession.slot[self.slot].set('tribConfigType', connection.channel, trafficType)
            except:
                pass
            if result != trafficType:
                raise BerTester.BerFailError
        self.reset(ip, slot, trib)

            
    def reset(self, ip, slot, trib):
        """
        Activates the PRBS on the specified trib, and resets the error count
        """
        #Turn on traffic generation, and reset the error count
        connection = self.get_connection(ip, slot, trib)
        try:
            inputBuf = chr(connection.channel) + "\x01"
            result = (self.berSession.slot[1].set('rmFaultDigitalLoopback', 0, -1) == -1)
            result &= (self.berSession.slot[self.slot].set('engTestInputBuffer', 0, inputBuf) == inputBuf)
            self.berSession.slot[self.slot].set('engTestFunction', 0, 9) == 9

            inputBuf = chr(connection.channel) + "\x02"
            result = (self.berSession.slot[self.slot].set('engTestInputBuffer', 0, inputBuf) == inputBuf)
            result &= (self.berSession.slot[self.slot].set('engTestFunction', 0, 9) == 9)
            
        except:
            result = False
        if not result:
            raise BerTester.BerFailError
        inst_str = "15.1.3.6.1.4.1.2509.7.4.1.4.4.2." + str(connection.channel) + ".2"
        connection.aisCount = int(self.berSession.slot[self.slot].get("eventState", inst_str))
        inst_str = "15.1.3.6.1.4.1.2509.7.4.1.4.4.1." + str(connection.channel) + ".1"
        connection.losCount = int(self.berSession.slot[self.slot].get("eventState", inst_str))
        
        #self.check(ip, slot, trib)
        self.stats["ErrorCount"] = 0


    def on(self, ip, slot, trib):
        """
        Activates PRBS on the specified trib
        """
        self.reset(ip, slot, trib)


    def off(self, ip, slot, trib):
        """
        Deactivates the PRBS on the specified trib
        """
        connection = self.get_connection(ip, slot, trib)
        result = 0
        try:
            inputBuf = chr(connection.channel) + "\x00"
            result = (self.berSession.slot[self.slot].set('engTestInputBuffer', 0, inputBuf) == inputBuf)
            result = (self.berSession.slot[self.slot].set('engTestFunction', 0, 9) == 9)
        except:
            result = False
        #if not result:
        #    raise BerTester.BerFailError

    def check(self, ip, slot, trib):
        """
        Returns the error count for the specified trib
        """
        connection = self.get_connection(ip, slot, trib)

        if connection.trib_type != self.tribType or \
           connection.trib_type == eTribType.TRIB_TYPE_UNKNOWN:
            raise BerTester.BerNotSupportedError

        try:
            inputBuf = chr(connection.channel) + "\x02"
            result = (self.berSession.slot[self.slot].set('engTestInputBuffer', 0, inputBuf) == inputBuf)
            result &= (self.berSession.slot[self.slot].set('engTestFunction', 0, 9) == 9)
            errStr = self.berSession.slot[self.slot].get('engTestOutputBuffer',0)
            errStr = errStr.strip(chr(0))
            self.stats["ErrorCount"] = int(errStr)
        except:
            result = False
        if not result:
            raise BerTester.BerFailError
        
        #Check for AIS or LOS alarm on trib
        alarmState = self.check_los(ip, slot, trib) or self.check_ais(ip, slot, trib)
           
        if not self.stats["ErrorCount"]:
            return alarmState
        return self.stats["ErrorCount"]

    def check_ais(self, ip, slot, trib):
        """
        checks to see if ais has been raised since the last call to reset()
        """
        connection = self.get_connection(ip, slot, trib)

        if connection.trib_type != self.tribType or \
           connection.trib_type == eTribType.TRIB_TYPE_UNKNOWN:
            raise BerTester.BerNotSupportedError

        alarmState = 0
        inst_str = "15.1.3.6.1.4.1.2509.7.4.1.4.4.2." + str(connection.channel) + ".2"
        alarmCount = int(self.berSession.slot[self.slot].get("eventState", inst_str))
        alarmActive = alarmCount % 2
        if alarmActive or (connection.aisCount != alarmCount):
            alarmState = -1

        return alarmState

    def check_los(self, ip, slot, trib):
        """
        checks to see if los has been raised since the last call to reset()
        """
        connection = self.get_connection(ip, slot, trib)

        if connection.trib_type != self.tribType or \
           connection.trib_type == eTribType.TRIB_TYPE_UNKNOWN:
            raise BerTester.BerNotSupportedError

        alarmState = 0
        inst_str = "15.1.3.6.1.4.1.2509.7.4.1.4.4.1." + str(connection.channel) + ".1"
        alarmCount = int(self.berSession.slot[self.slot].get("eventState", inst_str))
        alarmActive = alarmCount % 2
        if alarmActive or (connection.losCount != alarmCount):
            alarmState = -1

        return alarmState

    #STILL NEED TO BE IMPLEMENTED
    #def ais_on(self, ip, slot, trib):
    #def ais_off(self, ip, slot, trib):

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#
