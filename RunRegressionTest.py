#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/System/RunRegressionTest.py,

"""
Provides class for handling execution of a regression test
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import RegressionTest
import sys, traceback
import time, threading
from Modules import UniqueID
from Enum.eCapacity import eCapacity
from Enum.eModulation import eModulation
from Table.tCircuitType import tCircuitType
import os

class RunRegressionTest(object):
    """
    Class for handling execution of a regression test
    Responsible for controlling:
        Initialisation of test script
        Execution of test script
        Information collection for failed tests
        Result processing
        Clean-up after script completion
    """
    def __init__(self):
        """
        RunRegressionTest constructor
        """
        self.stopOnFail = True
        self.stopOnError = False
        #self.networkWrapper = None

    def __runMethod(self, method, *arguments):
        """
        Wrapper function for calling regression test methods
        Handles common code
        
        @type     method: class instance method
        @param    method: The instance method to be called
        @type  arguments: tuple
        @param arguments: The arguments to pass into the specified method
        @rtype:  eTestResult
        @return: The result from executing the specified method
        """
        result = False
        try:
            method(*arguments)
            result = 0
        except RegressionTest.TestFailError:
            result = 1
            # dump out syslogs to disk
            #self.storeLogs(self.local,self.remote)
        except RegressionTest.TestAbortError:
            result = 2
        except KeyboardInterrupt:
            raise
        except:
            result = 1
            self.log.error('Error Value : ' + str(sys.exc_info()[1]))
            self.log.error('Error Type  : ' + str(sys.exc_info()[0]))
            self.log.error('TraceBack   : ' + str(traceback.extract_tb(sys.exc_info()[2])))

            #self.storeLogs(self.local,self.remote)
            #raise
        
        return result

    # (TODO) decide where to put this code
    def restore_defaults(self,log, local, remote, testScript):
        """
        restore terminals to its default configuration, check alarms

        @type      log: syslog
        @param     log: log file
        @type    local: terminal session
        @param   local: local terminal
        @type   remote: terminal session
        @param  remote: remote terminal
        @rtype:  int
        @return: True if pass, or False if failed
        """
        import RestoreConfig
        from Modules import Timer
        
        print 'restore defaults'
        
        # check that we aren't about to do a soft reset
        localReset  = 0
        remoteReset = 0
        try:
            swReset = local.terminal.get('swManagerSoftReset', 1 )
            if int(swReset) != 2:
                localReset = 1
            swReset = remote.terminal.get('swManagerSoftReset', 1 )
            if int(swReset) != 2:
                remoteReset = 1
        except:
            pass

        # if local or remote terminals are marked to restart then wait for them
        wait = Timer.PeriodicWait('waiting for soft reset', 300, 10)
        while wait.remaining:

            if localReset:
                try:
                    local.terminal.get('swManagerSoftReset', 1)
                except:
                    localReset = 0
                
            if remoteReset:
                try:
                    remote.terminal.get('swManagerSoftReset', 1)
                except:
                    remoteReset = 0

            if localReset == 0 and remoteReset == 0:
                break

            wait.periodic()

        # time out while waiting for terminal to restart
        if not wait.remaining:
            log.error('timed out while waiting for terminal to restart, cannot run test')
            #log.abort(testScript.name)
            return False           
                    
        # wait to make sure we can access both terminals
        wait = Timer.PeriodicWait('waiting for terminals', 300, 10)
        while wait.remaining:

            # (TODO) check that we haven't aborted the test here    
            try:
                local.terminal.get('mfgDetailsInfoSerialNumber', 1)
                remote.terminal.get('mfgDetailsInfoSerialNumber', 1)
                # if we get here without raising an error we have passed
                break;
            except:
                pass

            wait.periodic()

        # timed out while waiting for terminal to boot
        if not wait.remaining:
            log.error('timed out while waiting for terminal to boot, cannot run test')
            #log.abort(testScript.name)
            return False


        # give time for alarms to raise, if there is no alarms after 30 seconds
        # then abort restore to default and continue testing
##        wait = Timer.PeriodicWait('waiting for any alarms to raise', 10, 10)
##        while wait.remaining:
##            
##            alarms = []            
##            alarms.append(local.terminal.alarms.status('terminal'))
##            alarms.append(remote.terminal.alarms.status('terminal'))
##            
##            raised = 0
##            
##            for alarm in alarms:
##                # if raised
##                if (alarm[0] % 2):
##                    # if severity < 4 (not warning)
##                    if (alarm[1] < 4):
##                        raised = 1
##
##            if raised:
##                break
##
##            wait.periodic()
##            
##        # no alarms are raised so return without restoring
##        if not wait.remaining:
##            print 'no alarms - restore aborted, continue test'
##            return True
##            
##        # create two restore threads one for each end of the link    
##        RestoreLocal = RestoreConfig.RestorerThread(local)
##        RestoreRemote = RestoreConfig.RestorerThread(remote)        
##        RestoreLocal.start()
##        RestoreRemote.start()
##            
##        # wait for restore to complete        
##        RestoreLocal.join()
##        RestoreRemote.join()
##
##        if RestoreLocal.exitStatus == False:
##            log.error('failed to restore local terminal, cannot start test')
##            return False
##        
##        if RestoreRemote.exitStatus == False:
##            log.error('failed to restore remote terminal, cannot start test')
##            return False
##        
##        # after restoring settings give time for alarms to raise, if there is no
##        # alarms after 30 seconds then assume everything is ok and continue
##        wait = Timer.PeriodicWait('waiting for any alarms to raise', 30, 10)
##        while wait.remaining:
##            
##            alarms = []            
##            alarms.append(local.terminal.alarms.status('terminal'))
##            alarms.append(remote.terminal.alarms.status('terminal'))
##            
##            raised = 0
##            
##            for alarm in alarms:
##                # if raised
##                if (alarm[0] % 2):
##                    # if severity < 4 (not warning)
##                    if (alarm[1] < 4):
##                        raised = 1
##
##            if raised:
##                break
##            
##            wait.periodic()
##            
##        # no alarms are raised so return without restoring
##        if not wait.remaining:
##            print 'no alarms after restore, continue test'
##            return True
##
##        # we have alarms so we need to wait to see if they will clear by themselves
##        # if the alarms do no clear after 300 seconds then abort the test
##        wait = Timer.PeriodicWait('alarms! waiting for any alarms to clear', 300, 10)
##        while wait.remaining:
##
##            alarms = []            
##            alarms.append(local.terminal.alarms.status('terminal'))
##            alarms.append(remote.terminal.alarms.status('terminal'))
##            
##            raised = 0
##            
##            for alarm in alarms:
##                # if raised
##                if (alarm[0] % 2):
##                    # if severity < 4 (not warning)
##                    if (alarm[1] < 4):
##                        raised = 1
##
##            # no alarms raised
##            if raised == 0:
##                break
##            
##            # update wait
##            wait.periodic()
##
##        # if we timeout then report the alarms
##        if not wait.remaining:
##            print 'check all alarms'
##        
##            # check what alarms we have on local terminal
##            #alarms_failed = 0
##            alarms = local.alarms.checkAll()
##            for x in alarms:
##                if x[1] < 4:
##                    log.error(self.local.address + ' local alarm raised: "' + str(x[0]) + '" severity : '+str(x[1]))
##                    #alarms_failed = 1
##                elif x[1] == 4:
##                    log.warning(self.local.address + ' local alarm raised: "' + str(x[0]) + '" severity : '+str(x[1]))
##                # don't worry about level 5 alarms at the moment
##
##            # check what alarms we have on remote terminal            
##            alarms = remote.alarms.checkAll()
##            for x in alarms:
##                if x[1] < 4:
##                    log.error(self.remote.address + ' remote alarm raised : "' + str(x[0]) + '" severity : '+str(x[1]))
##                    #alarms_failed = 1
##                elif x[1] == 4:
##                    log.warning(self.remote.address + ' remote alarm raised  : "' + str(x[0]) + '" severity : '+str(x[1]))
##                # don't worry about level 5 alarms at the moment
##                    
##            #if alarms_failed:
##            log.error('alarms are raised, cannot start test')
##            #log.abort(testScript.name)
##            return False

        return True        
            
        #---------------------------------------------------------------------------
        
    def runTest(self, log, testScript, networkWrapper, config, iterations = 1):
        """
        Controls initialisation, execution and post-processing for a regression test

        @type    testScript: RegressionTest
        @param   testScript: Instance of RegressionTest to be executed
        @type  networkWrapper: network object
        @param networkWrapper: information for radio network to be tested
        @type    iterations: int
        @param   iterations: The number of times the test should be run
        """
        #Create the syntactical wrapper for the hardware being tested
        self.local    = networkWrapper.local
        self.remote   = networkWrapper.remote

        self.log = log   
        testScript.log = log
        
        # generate a unique ID and assign it to our log, and testscript        
        self.uniqueID       = UniqueID.Generate()
        testScript.uniqueID = self.uniqueID
        log.setUniqueID(self.uniqueID)
            
        #iteration = 0
        message = "Radio link: " + networkWrapper.local.address + " <--> " + networkWrapper.remote.address
        log.cycle(message)
        log.test(testScript.name)

        #-------------------------Check Alarms-----------------------------------       
##        if not self.restore_defaults(log, self.local, self.remote, testScript):
##            # test failed, could not run
##            log.abort(testScript.name)
##            return
        #---------------------------------------------------------------------------
        
        try:
            swVersionLocal  = self.local.terminal.get('swDetailsVersion', 1)
            swVersionRemote = self.remote.terminal.get('swDetailsVersion', 1)
            log.swver(swVersionLocal + " <--> " + swVersionRemote)
        except:
            self.log.error('Error Value : ' + str(sys.exc_info()[1]))
            self.log.error('Error Type  : ' + str(sys.exc_info()[0]))
            self.log.error('TraceBack   : ' + str(traceback.extract_tb(sys.exc_info()[2])))

            log.fail(testScript.name)
            #self.storeLogs(self.local,self.remote)
            testScript.storeLogs()
            return


        try:

            localcapacity    = self.local.slot[self.local.racSlot].get('unityRmConfigCapacity', 0)
            localmodulation  = self.local.slot[self.local.racSlot].get('unityRmConfigModemModulation', 0)
            #localcircuittype = self.local.terminal.get('ctuUnitConfigCircuitType', 0)
##
            remotecapacity   = self.remote.slot[self.remote.racSlot].get('unityRmConfigCapacity', 0)
            remotemodulation = self.remote.slot[self.remote.racSlot].get('unityRmConfigModemModulation', 0)
            #remotecircuittype= self.remote.terminal.get('ctuUnitConfigCircuitType', 0)

            log.traffic(eCapacity[localcapacity] + " <--> " + eCapacity[remotecapacity])
            log.traffic(eModulation[localmodulation] + " <--> " + eModulation[remotemodulation])

        except:
           self.log.error('Error Value : ' + str(sys.exc_info()[1]))
           self.log.error('Error Type  : ' + str(sys.exc_info()[0]))
           self.log.error('TraceBack   : ' + str(traceback.extract_tb(sys.exc_info()[2])))

           log.fail(testScript.name)
            #self.storeLogs(self.local,self.remote)
           testScript.storeLogs()
           return
           
        
            #log.warning("couldn't retrieve sw version from terminal")
            #return
        #log.swver(swVersionLocal + " <--> " + swVersionRemote)

                
        #log.info("Test Script Initialisation")
        
        result = self.__runMethod(testScript.initScript, log, networkWrapper.local, networkWrapper.remote, config)

        if result == 0:
            # pass
            result = self.__runMethod(testScript.runTest, log, networkWrapper.local, networkWrapper.remote, config)
            if result == 0 or result == 2:
                # if self.errorTest() called before self.abortTest() or test completes after self.errorTest() called.
                if testScript.failedTest:
                    result = 1          

        else:
            log.alert('initialisation failed to complete, aborting test')
            result = 2
            
        # clean up test
        self.__runMethod(testScript.cleanUp, log, networkWrapper.local, networkWrapper.remote, config)

        # now based on the test result, pass, fail or abort the test
        if   result == 0:
            log.ok(testScript.name)
        elif result == 1:
            log.fail(testScript.name)
            testScript.storeLogs()
        elif result == 2:
            log.abort(testScript.name)
            
        self.processResults()
        
    def getFailureInfo(self, iteration, iterations, testResult):
        """
        Calls routines to generate test failure report
        """
        pass

    def processResults(self):
        """
        Calls routines to process test results
        """
        pass

if __name__ == "__main__":
    "RATS system support module: Cannot be run independently"

#

#
