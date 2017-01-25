#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/System/xtest_run_regression_test.py,

"""
Unit test for run_regression_test module
"""

import unittest, RegressionTest
from RunRegressionTest import RunRegressionTest
from X_mock_test import MockTest

class TestRunRegressionTest(unittest.TestCase):
    def setUp(self):
        self.runner = RunRegressionTest()
        self.hardware1 = [1, 2]
        self.hardware2 = [2, 3]

    def testExecute(self):
        """
        Check successful script execution
        Ensures test is initialised and executed the correct number of times
        """
        test = MockTest()
        #Check test pass
        self.runner.runTest(test, self.hardware1, 1)
        assert test.hardwareSpec == self.hardware1
        assert test.testFirstInitCount == 1
        assert test.testInitCount == 1
        assert test.testRunCount == 1
        #Check test pass on different hardware        
        self.runner.runTest(test, self.hardware2, 1)
        assert test.hardwareSpec != self.hardware1
        assert test.hardwareSpec == self.hardware2
        assert test.testFirstInitCount == 2
        assert test.testInitCount == 2
        assert test.testRunCount == 2
        #Check test completes specified number of iterationss
        self.runner.runTest(test, self.hardware2, 5)
        assert test.hardwareSpec != self.hardware1
        assert test.hardwareSpec == self.hardware2
        assert test.testFirstInitCount == 3
        assert test.testInitCount == 7
        assert test.testRunCount == 7

    def testInitScriptFailure(self):
        """
        Check test failure during script initialisation
        """
        test = MockTest()
        #Check test failure during script initialisation
        test.failMode = 11
        self.runner.runTest(test, self.hardware1)
        assert test.testRunCount == 0
        assert self.runner.testsFailed == 1
        assert self.runner.errorCount == 0
        #Check script failure during script initialisation
        test.failMode = 12
        self.runner.runTest(test, self.hardware1)
        assert test.testRunCount == 0
        assert self.runner.testsFailed == 1
        assert self.runner.errorCount == 1

    def testInitTestFailure(self):
        """
        Check test failure during test initialisation
        """
        test = MockTest()
        #Check test failure during test initialisation
        test.failMode = 21
        self.runner.runTest(test, self.hardware1)
        assert test.testRunCount == 0
        assert self.runner.testsFailed == 1
        assert self.runner.errorCount == 0
        #Check script failure during test initialisation
        test.failMode = 22
        self.runner.runTest(test, self.hardware1)
        assert test.testRunCount == 0
        assert self.runner.testsFailed == 1
        assert self.runner.errorCount == 1

    def testExecuteFailure(self):
        """
        Check test failure during test execution
        """
        test = MockTest()
        #Check test failure during test execution
        test.failMode = 31
        self.runner.runTest(test, self.hardware1)
        assert test.testRunCount == 1
        assert self.runner.errorCount == 0
        assert self.runner.testsFailed == 1
        #Check script failure during test execution
        test.failMode = 32
        self.runner.runTest(test, self.hardware1)
        assert test.testRunCount == 2
        assert self.runner.testsFailed == 1
        assert self.runner.errorCount == 1

if __name__ == "__main__":
    unittest.main()

#
# $Log: xtest_run_regression_test.py,v $
# Revision 1.1.1.1  2006/11/07 02:32:49  mpenman
# Imported sources
#
#    