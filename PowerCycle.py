#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Scripts/PowerCycle.py,

"""
   Test Name     : PowerCycle.py
   Description   : Attempts to power cycle a terminal
   Requirements  :  
"""

#--------------------------------------------------------------------------
# imports
#--------------------------------------------------------------------------
import time
from   System.RegressionTest import RegressionTest
from   Helper  import *

class TestScript(RegressionTest):
    """
    RATS Test: Power Cycle
    """
       
    #----------------------------------------------------------------------
    #Initialisation specific to instance of test
    #----------------------------------------------------------------------
    def __init__(self):
        """
        Object initialisation
        """
        RegressionTest.__init__(self)
        self.name = "Power Cycle"
        
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

    #----------------------------------------------------------------------
    #Method containing the test
    #----------------------------------------------------------------------
    def runTest(self, log, local, remote, config):
        """
        Test Script execution
        """
        local.power.on()
        local.power.off()

        #local.odu[1].power.on()
        #local.odu[1].power.off()        
        
    #----------------------------------------------------------------------
    # cleanUp
    #----------------------------------------------------------------------
    def cleanUp(self, log, local, remote, config):
        """
        Restore all modified variables
        """
        pass
    

if __name__ == "__main__":
    print "RATS regression test script: Cannot be run independently"

#
