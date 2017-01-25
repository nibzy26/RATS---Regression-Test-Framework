#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Scripts/DateTimeSetManual.py,

"""
   Test Name: Telnet.py

   Description: check Nms over the link
                                   
   Requirements: Working link.
"""

#--------------------------------------------------------------------------
# imports
#--------------------------------------------------------------------------
import time
import random
from System.RegressionTest import RegressionTest
from Snmp import SnmpManager
from Helper import *
from Modules import Timer

TIME_SET_DELAY = 1

class TestScript(RegressionTest):
    
    #----------------------------------------------------------------------
    #Initialisation specific to instance of test
    #----------------------------------------------------------------------
    def __init__(self):
        """
        Object initialisation
        """
        RegressionTest.__init__(self)
        self.name = "Manual Date Time Set Test"
        # end of initialisation

    #----------------------------------------------------------------------
    # Initialisation for test script execution
    #----------------------------------------------------------------------
    def initScript(self, log, local, remote, config):
        """
        Test Script initialisation
        Prepare for test by storing any previous configuration details
        """
        pass
        
    def convertToDateTimeStr(self, timeStruct):
        # put things in right order
        yearHigh = timeStruct[0] >> 8
        yearLow = timeStruct[0] & 0xFF
        month = timeStruct[1]
        day = timeStruct[2]
        hour = timeStruct[3]
        minutes = timeStruct[4]
        seconds = timeStruct[5]
        deci_sec = 0
        dirUTC = 0
        hrFromUTC = 0
        minFromUTC = 0
        
        # create SNMP DateTime string format
        dateAndTimeStr = chr(yearHigh) + chr(yearLow) + chr(month) + chr(day) + chr(hour) + chr(minutes) + chr(seconds)
        dateAndTimeStr = dateAndTimeStr + chr(deci_sec) + chr(dirUTC) + chr(hrFromUTC) + chr(minFromUTC)
        
        return dateAndTimeStr
        
    def convertToDateTimeStruct(self, timeStr):
        # we know where things are in SNMP DateTime string, so now make it into time struct
        timeStruct = [ ((ord(timeStr[0]) << 8) & 0xFF00) | ord(timeStr[1]),
                       ord(timeStr[2]),
                       ord(timeStr[3]),
                       ord(timeStr[4]),
                       ord(timeStr[5]),
                       0,
                       0,
                       0]
        return timeStruct
        
    def getRandomDateAndTimeStr(self):
        yearMax = 2010
        yearMin = 1970
        
        # generate random date & time
        year = random.randint(yearMin, yearMax)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        
        dateAndTimeStr = self.convertToDateTimeStr([year, month, day, hour, minutes, seconds])
        
        return dateAndTimeStr
        
    def compareDateTimeStr(self, new, old):
        # compare only year, month, day, hour as minutes and seconds can change during test
        if (new[0:4] != old[0:4]):
            return False
        
        return True
        
    #----------------------------------------------------------------------
    #Method containing the test
    #----------------------------------------------------------------------
    def runTest(self, log, local, remote, config):
        """
        Test Script execution
        """       
        LocalFail = "Fail"
        RemoteFail = "Fail"
        
        try:
            # get random time
            dateAndTimeStr = self.getRandomDateAndTimeStr()
            
            # set time
            local.terminal.set("hrSystemDate", 0, dateAndTimeStr)
            Timer.Wait("Date and Time set delay", TIME_SET_DELAY)
            
            # get new time
            newTime = local.terminal.get("hrSystemDate", 0)
            print "set", self.convertToDateTimeStruct(dateAndTimeStr)
            print "new", self.convertToDateTimeStruct(newTime)
            
            # see if it changed
            if self.compareDateTimeStr(newTime, dateAndTimeStr) == True:
                LocalFail = "Pass"
            
            # get random time
            dateAndTimeStr = self.getRandomDateAndTimeStr()
            
            # set time
            remote.terminal.set("hrSystemDate", 0, dateAndTimeStr)
            Timer.Wait("Date and Time set delay", TIME_SET_DELAY)
            
            # get new time
            newTime = remote.terminal.get("hrSystemDate", 0)
            print "set", self.convertToDateTimeStruct(dateAndTimeStr)
            print "new", self.convertToDateTimeStruct(newTime)
            
            # see if it changed
            if self.compareDateTimeStr(newTime, dateAndTimeStr) == True:
                RemoteFail = "Pass"
        except:
            raise

        if LocalFail == "Fail" or RemoteFail == "Fail":
            self.failTest("RSL: Local=" + LocalFail + ", Remote=" + RemoteFail)
        
        # done end of test

    #----------------------------------------------------------------------
    # cleanUp
    #----------------------------------------------------------------------
    def cleanUp(self, log, local, remote, config):
        """
        Restore all modified variables
        """        
        # restore terminals to local time
        timeNow = time.localtime(time.time())
        
        timeNowStr = self.convertToDateTimeStr(timeNow)
        
        local.terminal.set("hrSystemDate", 0, timeNowStr)
        Timer.Wait("Date and Time set delay", TIME_SET_DELAY)
        print "set", self.convertToDateTimeStruct(timeNowStr)
        print "new", self.convertToDateTimeStruct(local.terminal.get("hrSystemDate", 0))
        remote.terminal.set("hrSystemDate", 0, timeNowStr)
        Timer.Wait("Date and Time set delay", TIME_SET_DELAY)
        print "set", self.convertToDateTimeStruct(timeNowStr)
        print "new", self.convertToDateTimeStruct(remote.terminal.get("hrSystemDate", 0))
        
if __name__ == "__main__":
    print "RATS regression test script: Cannot be run independently"

