#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/System/JobRunner.py,

"""
Jobrunner, runs a job on the provided network. handles threading and timeouts of a single job
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

from Snmp import SnmpManager
from SysLog import SysLog
import RunRegressionTest
#from Traffic import TribTraffic, BerManager
#from System  import Config
from Modules import KillableThread
from Modules import Timer
from Modules import UniqueID
from Modules import Status

import time
import datetime
import RestoreConfig
#from Modules import Alarms
from Network import NetworkManager

#
# dump terminal configuration to the log
#
def showSetup(node, log):
    """
    querys the terminal (indicated by node) and dumps it's configuration to the log

    @type   node: 
    @param  node: terminal session to use
    @type   log :
    @param  log : log to write terminal configuration to
    """
    unitType  = "XXX"
    hsc       = -1
    serial    = "XXX"
    part      = "XXX"
    desc      = "XXX"

    try:
        unitType  = node.terminal.get('mfgDetailsInfoUnitType', 1, False)
        hsc       = node.terminal.get('mfgDetailsHscNumber', 1, False)
        serial    = node.terminal.get('mfgDetailsInfoSerialNumber', 1, False)
        part      = node.terminal.get('mfgDetailsInfoPartNumber', 1, False)
        desc      = node.terminal.get('mfgDetailsInfoUnitDescription', 1, False)
    except:
        #log.fail("couldn't retrieve mfgDetails from terminal")
        return

    log.config('----------------------------------------------------------------------------------------------')
    log.config('Terminal : %s %-12s HSC : %-3d Serial : %-16s Part : %-16s' % ( str(node.address), str(desc), int(hsc), str(serial),str(part) ))

    node.community ="odu1"

    try:
        unitType  = node.get('mfgDetailsInfoUnitType', 1, False)
        hsc       = node.get('mfgDetailsHscNumber', 1, False)
        serial    = node.get('mfgDetailsInfoSerialNumber', 1, False)
        part      = node.get('mfgDetailsInfoPartNumber', 1, False)
        desc      = node.get('mfgDetailsInfoUnitDescription', 1, False)
    except:
        #log.fail("couldn't retrieve mfgDetails for odu1")
        return
        
    log.config('%-12s HSC : %-3d Serial : %-16s Part : %-16s' % ( str(desc), int(hsc), str(serial),str(part) ))
    log.config('----------------------------------------------------------------------------------------------')
        
    log.config('Slot | Description       | Type  | Serial Number      | Part Number       | HSC')
        
    # check the slots to see which are empty        
    for i in range(1,12):
        try:
            node.community = "terminal"
            slotType = node.get('slotConfigDetectedType', i , False)
            if slotType != 0:
                node.community = 'slot' + str(i)
                #unitType  = node.get('mfgDetailsInfoUnitType', 1, False)
                hsc       = node.get('mfgDetailsHscNumber', 1, False)
                serial    = node.get('mfgDetailsInfoSerialNumber', 1, False)
                part      = node.get('mfgDetailsInfoPartNumber', 1, False)
                desc      = node.get('mfgDetailsInfoUnitDescription', 1, False)
                log.config(' %02d  |  %-16s |  %3d  |  %-16s  |  %-16s | %3d' % (i, str(desc), int(slotType), str(serial), str(part),int(hsc)))
        except:
            #log.fail("couldn't retrieve mfgDetails for slot " + str(i))
            return



class JobRunner(KillableThread.KillableThread):
    """
    JobRunner : The JobRunner is responsible for running a single job within its own thread
                multiple JobRunner objects may be created to run multiple jobs simultaneously.
                
       ** Network resources may be shared however we must make sure that the correct locking
          procedures are used **
    """
    
    # test thread (sub thread)
    class TestThread(KillableThread.KillableThread):
        """
        JobRunner.TestThread : Thread created for every test that is required, only one instance
                               of this thread should be created at a single point in time. the purpose
                               of this thread is to allow the test to run in its own thread and not block
                               the JobRunner thread. This allows the JobRunner thread to do other tasks such
                               as monitor the time elapsed and kill the TestThread in the case that it doesn't
                               complete in the expected time.
        """
        def __init__(self, parent, testScript, hwInfo, jobId):
            """
            JobRunner.TestThread constructor
        
            @type  parent     : JobRunner
            @param parent     : reference to JobRunner object who is the parent of this thread
            @type  testScript : string
            @param testScript : name of the test script to run
            @type  hwInfo     : Network()
            @param hwInfo     : network information
            """            
            KillableThread.KillableThread.__init__(self)
            self.log        = parent.log
            self.testScript = testScript
            self.hwInfo     = hwInfo
            self.config     = parent.config
            self.jobId      = jobId
            
        def run(self):
            self.testScript.status.bind(self.jobId)
            self.log.bind()
            runner = RunRegressionTest.RunRegressionTest()
            runner.runTest(self.log, self.testScript, self.hwInfo, self.config)
            self.testScript.status.unbind()

        def terminate(self):
            self.testScript.status.unbind()
            KillableThread.KillableThread.terminate(self)
            
                
    # runner
    def __init__(self, job, config, testinfo ):
        """
        JobRunner constructor
        
        @type  network  : network infomation type
        @param network  : stores the information about the network to run this job on
        @type  tests    : list of strings
        @param tests    : a list of tests to run on this network
        @type  config   : dictionary
        @param config   : configuration information for the rats system loaded from rats.conf
        @type  testinfo : dictionary
        @param testinfo : test compatibility information loaded from test.conf
        """
        KillableThread.KillableThread.__init__(self)
        self.network  = job.network
        self.tests    = job.tests
        self.username = job.username
        self.batch    = job.batch       # batch number for this job, this tells the job runner where
                                        # to store the results
        self.testinfo = testinfo
        self.status   = 0
        self.config   = config

        # (TODO RELOAD TESTS.CONF, perhaps do this per test?)
        #self.config  = Config.loadConfig('tests.conf')

        self.log     =  None
        self.activeTest = None
        self.Timer    = Timer.Timer()
        self.TotalTimer = Timer.Timer()
        self.testName = 'None'
        self.fileName = ''
        self.terminated = False
        self.uniqueID = UniqueID.Generate()
    
    def statusTest(self):
        """
        statusTest  : return a string containing status information from the JobRunner
        """
        status = Status.status()

        return str(self.status) + ' of ' + str(len(self.tests)) + ' : ' + self.testName + ' (' + \
               str(self.Timer.elapsed()) + ')' + ' (' + str(self.TotalTimer.elapsed()) + ')' + '\n      ' + status.get(self.uniqueID)

    # stop called by operator
    def haltTest(self):
        """
        haltTest    : halt the running test and terminate job
        """
        if self.log:
            self.log.warning('halting job (forced)')
        
        if self.activeTest != None:
            if self.activeTest.isAlive():
                self.activeTest.terminate()
       
        self.terminated = True

    # stop called by operator
    def haltAfterTest(self):
        """
        haltAfterTest    : halt job at the next safe point
        """
        if self.log:
            self.log.warning('halting job after the next test')
            
        self.terminated = True

        
    def run(self):
        """
        JobRunner run method : called when JobRunner.start() is called        
        """
        _manager = SnmpManager.SnmpManager()
        self.TotalTimer.stop()

        # (NETWORK MANAGER)
        _nm = NetworkManager.NetworkManager()
        interface = _nm.createInterface(self.network)

        if interface == None:
            print '****** interface == NONE *****'
            return
        
        # creates the file (log-yyyy-mm-dd-aaa.bbb.ccc.ddd-aaa.bbb.ccc.ddd.txt)        
        self.log = SysLog.SystemLog(interface.local.address+'-'+interface.remote.address, self.batch)
      
        # scan terminals and dump their hardware set-up to the log
        showSetup(interface.local,self.log)
        showSetup(interface.remote,self.log)
  
        self.TotalTimer.start()

        # if terminated before startup
        if self.terminated:
            self.log.closeLog()
            #self.tlog.close()
            self.TotalTimer.stop()
            return
        
        for test in self.tests:
    
            #self.log.info("_________________________________________________")
            # read test info from tests dictionary
            testscript = "Scripts." + self.testinfo[test]['script']
            try:
                mod = __import__(testscript, globals(), locals(), [''])
            except ImportError:
                print 'failed to import script', testscript
                continue
            
            # reload module, updating changes to scripts
            try:
                reload(mod)
            except:
                print '!!!!!!!!!!!!!! reload error.... (TODO) !!!!!'
                continue
            
            testScript = mod.TestScript()

            # setup interface, in case we fail before the testScripts.initScript method is run.            
            testScript.networkWrapper = interface
            
            # update status information here
            self.status += 1
            self.testName = test
            
            # start the test thread            
            self.activeTest = self.TestThread(self, testScript, interface, self.uniqueID)
            self.activeTest.start()

            self.Timer.start()

            # this timeout value would be loaded from the testinfo
            timeout = 60 * 60 * 6 # 3 hours

            while (self.terminated == False) or (self.activeTest.isAlive()):
                # check timeout expired?
                if self.activeTest.isAlive():
                
                    if self.Timer.elapsed() >= timeout:
                        # timeout!! kill thread and log
                        self.activeTest.terminate()
                        self.log.fail('test timed out, terminated')
                        try:
                            print '************ ATTEMPTING TO CLEAN UP JOB *******'
                            testScript.cleanUp()
                        except:
                            pass
                        
                        break
                        
                    else:
                        # sleep / yield?
                        time.sleep(1)
                else:
                    # finished test
                    break

            # wait for thread to exit before continuing
            self.activeTest.join()
            self.Timer.stop()

            # log trace log to job log
            #testScript.appendLogs(self.tlog)
            
            if self.terminated:
                self.testName = 'Aborted'
                #if self.log:
                #    self.log.warning('tests aborted')
                try:
                    print '************ ATTEMPTING TO CLEAN UP JOB *******'
                    testScript.cleanUp()
                except:
                    pass
                break

        # update test names
        if self.terminated:
            self.testName = 'Aborted'
            if self.activeTest:
                self.activeTest.join()
        else:
            self.testName = 'Finished'
            
        _nm.unlockNetwork(self.network)
          
        if self.log:            
            self.log.closeLog()
        #self.tlog.close()
        self.TotalTimer.stop()
  
