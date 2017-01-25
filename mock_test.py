#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/System/mock_test.py,

"""
Mock test script object used for unit testing
"""

import RegressionTest

class MockTest(RegressionTest.RegressionTest):
    def __init__(self):
        #These variables are to aid unit testing, and do not exist in the standard test class.
        self.failMode = 0
        self.testRunCount = 0
        self.testInitCount = 0
        self.testFirstInitCount = 0
        self.logger = None
        self.hardwareSpec = None
        self.networkWrapper = None

    #This method is to aid unit testing, and does not exist in the standard test class.
    def setFailMode(self, failMode):
        """
        Used to set failure mode
            Failmode:
                0 = No fail
                1 = Test fail
                2 = Script fail
            SectionFail:
                10 = Script initialisation
                20 = Test initialisation
                30 = Test execution
            Combine the different values to control when the test fails
        """
        self.failMode = failMode
        
    def initScript(self, logger, hardwareSpec, networkWrapper):
        self.logger = logger
        self.hardwareSpec = hardwareSpec
        self.networkWrapper = networkWrapper
        self.testFirstInitCount += 1
        if (self.failMode/10) == 1:
            if (self.failMode%10) == 1:
                raise RegressionTest.TestFailError, "Simulated test failure during script initialisation"
            elif (self.failMode%10) == 2:
                raise RuntimeError, "Simulated script failure (unhandled error during script initialisation)"

    def initTest(self):
        self.testInitCount += 1
        if (self.failMode/10) == 2:
            if (self.failMode%10) == 1:
                raise RegressionTest.TestFailError, "Simulated test failure during test initialisation"
            elif (self.failMode%10) == 2:
                raise RuntimeError, "Simulated script failure (unhandled error during test initialisation)"

    def runTest(self):
        """Used to simulate a script being run"""
        self.testRunCount += 1
        if (self.failMode/10) == 3:
            if (self.failMode%10) == 1:
                raise RegressionTest.TestFailError, "Simulated test failure during test execution"
            elif (self.failMode%10) == 2:
                raise RuntimeError, "Simulated script failure (unhandled error during test execution)"

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#
