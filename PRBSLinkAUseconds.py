#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Scripts/PRBSLinkAUseconds.py,

"""
   Test Name: PRBSLinkAUseconds.py

   Description: gets the Avaliable/Unavaliable seconds count before and after muting the transmitter at the remote end 
   Assumptions:  RAC in slot 1 , DAC in slot 2                                
   Requirements: Working link.
"""

#--------------------------------------------------------------------------
# imports
#--------------------------------------------------------------------------
import time
from System.RegressionTest import RegressionTest
from Snmp import SnmpManager
from Helper import *
from Modules import Timer
from Enum.eCapacity import eCapacity
from Enum.eModulation import eModulation
from Table.tCircuitType import tCircuitType

PRBS_DELAY = 10
PRBS_TEST_DURATION = 60

prbs_params = [ 
#                "tribFaultLinkTestPattern",
#                "tribFaultLinkTestPatternLoss",
                "tribFaultLinkTestBitErrorCount",
                "tribFaultLinkTestBitErrorRatio",
                "tribFaultLinkTestErroredSeconds",
#                "tribFaultLinkTestErroredSecondsRatio",
                "tribFaultLinkTestSeverelyErroredSeconds",
#                "tribFaultLinkTestSeverelyErroredSecsRatio",
#                "tribFaultLinkTestAvailableTime",
                "tribFaultLinkTestUnavailableTime",
#                "tribFaultLinkTestElapsedTime",
#                "tribFaultLinkTestPackedData",
               ]
               
prbs_summary = "tribFaultLinkTestSummary"

class TestScript(RegressionTest):
    
    #----------------------------------------------------------------------
    #Initialisation specific to instance of test
    #----------------------------------------------------------------------
    def __init__(self):
        """
        Object initialisation
        """
        RegressionTest.__init__(self)
        self.name = "PRBSLinkAUseconds Test "
        # end of initialisation

    #----------------------------------------------------------------------
    # Initialisation for test script execution
    #----------------------------------------------------------------------
    def initScript(self, log, local, remote, config):
        """
        Test Script initialisation
        Prepare for test by storing any previous configuration details
        """
               
        
        local.slot[2].set("tribFaultLinkTestEnabled", 1, 0)
        remote.slot[2].set("tribFaultLinkTestEnabled", 1, 0)
        Timer.Wait("PRBS off", PRBS_DELAY)
        
    #----------------------------------------------------------------------
    #Method containing the test
    #----------------------------------------------------------------------
    def runTest(self, log, local, remote, config):
        """
        Test Script execution
        """

        
        log.info("Turning on PRBS")
        local.slot[2].set("tribFaultLinkTestEnabled", 1, -1)
        #remote.slot[2].set("tribFaultLinkTestEnabled", 1, -1)
        Timer.Wait("waiting ... ", 10)
        print "  "
        

        localResult = None
        remoteResult = None

        print remote.address

        U_seconds = local.slot[2].get("tribFaultLinkTestUnavailableTime", 1)   # Get Unava Time
        log.info("Unavailable Time is  " + str(U_seconds))
        
        Timer.Wait("waiting...", 4)
        A_seconds = local.slot[2].get("tribFaultLinkTestAvailableTime", 1)     # Get Ava Time
        log.info("Available Time is  " + str(A_seconds))
        
        Timer.Wait("waiting ..", 4)
        
        U_seconds = local.slot[2].get("tribFaultLinkTestUnavailableTime", 1)   # Get Unava Time
        log.info("Unavailable Time is  " + str(U_seconds))
        
        Timer.Wait("waiting ... ", 4)
        A_seconds = local.slot[2].get("tribFaultLinkTestAvailableTime", 1)     # Get Ava Time
        log.info("Available Time is  " + str(A_seconds))



        remote.slot[1].set("rfFaultTxMute", 0, -1)                             # Mute the Transmitter  *** THE REMOTE END ONE ***
        log.info(" After Muting the Transmitter on remote End ... ")
        Timer.Wait("waiting ...", 16)
        
        A_seconds = local.slot[2].get("tribFaultLinkTestAvailableTime", 1)     # Check that avaliable seconds have stopped incrementing
                                                                               # Allow few seconds for Muting
        log.info("Available Time is  " + str(A_seconds))
        AvaliableCheckA = A_seconds
        Timer.Wait("Waiting ... ", 7)
        U_seconds = local.slot[2].get("tribFaultLinkTestUnavailableTime", 1)   # Get Unava Time
        log.info("Unavailable Time is  " + str(U_seconds))
        Unavaliable_CheckA = U_seconds
        Timer.Wait("Waiting ... ", 7)
        A_seconds = local.slot[2].get("tribFaultLinkTestAvailableTime", 1)     # Check that avaliable seconds have stopped incrementing
        log.info("Available Time is  " + str(A_seconds))
        AvaliableCheckB = A_seconds
        if (AvaliableCheckB > AvaliableCheckA):
            self.errorTest("Error :Avaliable seconds count should not increase") 
        Timer.Wait("waiting ... ", 3)
        
        U_seconds = local.slot[2].get("tribFaultLinkTestUnavailableTime", 1)   # Get Unava Time
        log.info("Unavailable Time is  " + str(U_seconds))
        Unavaliable_CheckB = U_seconds

        if (Unavaliable_CheckB <= Unavaliable_CheckA):                         # Error, if Unavaliable seconds count is NOT increasing 
            self.errorTest(" Unavaliable seconds count Should increase ")
            
        remote.slot[1].set("rfFaultTxMute", 0, 0)                              # UN-Mute the Transmitter
        log.info(" Un -Muting the Transmitter on Remote End... ")
        
        Timer.Wait("waiting ... ", 16)

        A_seconds = local.slot[2].get("tribFaultLinkTestAvailableTime", 1)   # Check that avaliable seconds incrementing again
        log.info( "Available Time is  " + str(A_seconds))
        
        Timer.Wait("waiting", 7)
        U_seconds = local.slot[2].get("tribFaultLinkTestUnavailableTime", 1)     # Get Unava Time 
        log.info("Unavailable Time is  " + str(U_seconds))
        UnavaliableCheckA = U_seconds
        Timer.Wait("waiting ... ", 7)

        A_seconds = local.slot[2].get("tribFaultLinkTestAvailableTime", 1)     # Check that avaliable seconds incrementing again 
        log.info("Available Time is  " + str(A_seconds))
        
        U_seconds = local.slot[2].get("tribFaultLinkTestUnavailableTime", 1)   # Get Unava Time again
        log.info("Unavailable Time is  " + str(U_seconds))
        UnavaliableCheckB = U_seconds
        if (UnavaliableCheckB > UnavaliableCheckA):
            self.errorTest("Error: Unavaliable seconds count should not increase ")

        # done end of test

    #----------------------------------------------------------------------
    # cleanUp
    #----------------------------------------------------------------------
    def cleanUp(self, log, local, remote, config):
        """
        Restore all modified variables
        """
        log.status("Clean up")
        
               
        local.slot[2].set("tribFaultLinkTestEnabled", 1, 0)
        #remote.slot[2].set("tribFaultLinkTestEnabled", 1, 0)
        Timer.Wait("PRBS off", PRBS_DELAY)

if __name__ == "__main__":
    print "RATS regression test script: Cannot be run independently"

#
