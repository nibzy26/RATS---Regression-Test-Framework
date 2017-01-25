#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/System/RegressionTest.py,

"""
Abstract base class module for RATS regression test scripts
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import httplib
import StringIO

from Modules import Status
from datetime import datetime
import os

# helper functions
#from Helper import *

class RegressionTestError(Exception):
    """
    Base class for regression test exceptions
    """
    pass


class TestFailError(RegressionTestError):
    """
    Exception to be raised when a regression test fails
    """

    def __init__(self, reason=""):
        """
        TestFailError exception constructor
        
        @type  reason: string
        @param reason: The reason for which the test is considered to have failed
        """
        self.reason = reason

    def __str__(self):
        return repr(self.reason)

class TestAbortError(RegressionTestError):
    """
    Exception to be raised when a regression test is aborted mid test
    """

    def __init__(self, reason=""):
        """
        TestAbortError exception constructor
        
        @type  reason: string
        @param reason: The reason for which the test was aborted
        """
        self.reason = reason

    def __str__(self):
        return repr(self.reason)
    

class RegressionTest(object):
    """
    Abstract base class for regression test scripts
    Default methods provided should be overridden by individual test script classes
    """
    
    def __init__(self):
        """
        Regression test constructor
        """
        self.failedTest = False
        self.name = "Name of test not specified"
        self.uniqueID = ""
        self.status = Status.status()
        self.log = None
        
    def initScript(self, log, local, remote, config):
        """
        Test script initialisation. Called ONCE before test is executed
        
        @type          log: log
        @param         log: Instance of L{log} class to be used for test log output
        @type        local: object, interface
        @param       local: Interface object for the local terminal
        @type       remote: object, interface
        @param      remote: Interface object for the remote terminal
        @type       config: Dictionary
        @param      config: Dictionary containing test configuration parameters
        """
        pass
        
    def runTest(self, log, local, remote, config):
        """
        Test script :  Main test code to be executed
        
        @type          log: log
        @param         log: Instance of L{log} class to be used for test log output
        @type        local: object, interface
        @param       local: Interface object for the local terminal
        @type       remote: object, interface
        @param      remote: Interface object for the remote terminal
        @type       config: Dictionary
        @param      config: Dictionary containing test configuration parameters
        """
        pass

    def cleanUp(self, log, local, remote, config):
        """
        Post-test clean up
        Called after test has finished
                
        @type          log: log
        @param         log: Instance of L{log} class to be used for test log output
        @type        local: object, interface
        @param       local: Interface object for the local terminal
        @type       remote: object, interface
        @param      remote: Interface object for the remote terminal
        @type       config: Dictionary
        @param      config: Dictionary containing test configuration parameters
        """
        pass

    def abortTest(self, reason):
        """
        Called when a test is aborted. Test execution will be stopped.
        Test should indicate the reason for aborting

        @type    reason: string
        @param   reason: Descriptive reason why the test has been aborted
        """
        self.log.error(reason)
        raise TestAbortError, reason
    
    def failTest(self, reason):
        """
        Called when a test fails. Test execution will be stopped.
        Test should indicate the reason for failure

        @type    reason: string
        @param   reason: Descriptive reason why the test is considered to have failed
        """
        self.failedTest = True
        self.log.error(reason)
        raise TestFailError, reason
    
    def errorTest(self, reason):
        """
        Called when an error is detected during a test, but test execution should continue.
        Test should indicate the reason for error

        @type    reason: string
        @param   reason: Descriptive reason why the test is considered to be errored
        """
        self.failedTest = True
        self.log.error(reason)

    def passTest(self):
        """
        Called when a test passes successfully
        """
        self.failedTest = False


    def __retrieveLog(self, address):
        """
        connect to http server on radio and download cfg-active file
        """
        try:
            conn = httplib.HTTPConnection(address)
            conn.request("GET", "/logread")
            res = conn.getresponse()

            if res.status != 200 and res.reason != "OK":
                conn.close()
                #self.failTest('http error returned from terminal '+str(res.status))
                return None

            logData = res.read()
            logRead = StringIO.StringIO(logData)
            conn.close()

            return logRead
    
        except:
            return None


    def __storeLog(self, node):
        """
        store the trace log for a single node to disk
        """
        year          = str(datetime.today().strftime("%Y"))
        month         = str(datetime.today().strftime("%m"))
        day           = str(datetime.today().strftime("%d"))
        
        dirpath = "./logs/"+year+"/"+month+"/"+day+"/"+self.log.batchId
        #dirpath = "./logs/"+self.log.batchId
        
        try:
            os.makedirs(dirpath)
        except:
            pass
                
        logData = self.__retrieveLog(node.address)

        if logData != None:
            try:
                fp = open(dirpath+'/'+'tlog-'+self.uniqueID+'-'+str(node.address)+'.txt', 'wt')        
        
                for line in logData:
                    fp.write(line)
    
                fp.close()

            except:
                print 'failed to create file', 'tlog-'+self.uniqueID+'-'+str(node.address)+'.txt'
                
                
    def storeLogs(self):
        """
        Dump both local and remote syslogs to disk
        """
        self.__storeLog(self.networkWrapper.local)
        self.__storeLog(self.networkWrapper.remote)


    def appendLogs(self, fp):
        """
        Dump logs to the end of a preexisting file
        """
        logData = self.__retrieveLog(self.networkWrapper.local.address)

        if logData != None:

            fp.write("--------=======--------========------======-------======")
            fp.write(str(self.networkWrapper.local.address))
            fp.write("--------=======--------========------======-------======\n")
           
            for line in logData:
                fp.write(line)


        logData = self.__retrieveLog(self.networkWrapper.remote.address)        
        if logData != None:

            fp.write("--------=======--------========------======-------======")
            fp.write(str(self.networkWrapper.remote.address))
            fp.write("--------=======--------========------======-------======\n")
        
            for line in logData:
                fp.write(line)

 
if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#
