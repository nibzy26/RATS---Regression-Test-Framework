#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/System/TestTemplate.py,

"""
Template for regression test scripts
See DocReg #3214 for detailed information on creating test scripts
"""

__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

from System.RegressionTest import RegressionTest
# -----------------------------------------------------------------------
# Insert test specific imports here
# -----------------------------------------------------------------------

class TestName(RegressionTest):
    """
    Description of test
    """

    def __init__(self):
        """
        Description of instance constructor method
        """
        RegressionTest.__init__(self)
        #-----------------------------------------------------------------------
        # Insert any specialised instance initialisation code here
        self.name = "Insert Test Name Here"
        # -----------------------------------------------------------------------
  
    def initScript(self, log, local, remote, config):
        """
        Description of test script initialisation
        """
        #-----------------------------------------------------------------------
        # Insert test script initialisation code here
        # Will be executed before test is executed
        #-----------------------------------------------------------------------

    def runTest(self, log, local, remote, config):
        """
        Description of main test
        """
        #-----------------------------------------------------------------------
        #       Insert main test code here
        pass
        #-----------------------------------------------------------------------

    def cleanUp(self, log, local, remote, config):
        """
        Description of post-test clean up.
        """
        #-----------------------------------------------------------------------
        # Insert test clean-up code here
        # Will be executed ONCE after the test has completed or when the test fails
        pass
        #-----------------------------------------------------------------------

if __name__ == "__main__":
    print "RATS system regression test script: Cannot be run independently"

#
