#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/SysLog/SysLog.py,

"""
System Log module
Provides class for outputting messages to a system log file and/or the screen.
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

from time import strftime
from Terminal import TerminalControl
from datetime import datetime
from Modules import Status
import os, threading

class SystemLog(object):
    """
    Class to implement system log.
    Provides methods for specifying type of message to be output.
    """
    #            TAG         Log?    Status?  Format
    _tagTable = {"SWVER"  : [True ,  False,   ("magenta", "bold")],
                 "TEST"   : [True ,  False,   ("yellow",  "bold")],
                 "INFO"   : [False,  True,    ("white",   "dim" )],
                 "STATUS" : [False,  False,   ("white",   "bold")],
                 "CONFIG" : [True ,  True,    ("blue",    "bold")],
                 "TRAFFIC": [True ,  True,    ("magenta",    "bold")],
                 "MEASURE": [True ,  False,   ("cyan",    "dim" )],
                 "WARNING": [False,  False,   ("yelow",   "dim" )],
                 "ALERT"  : [True ,  False,   ("red",     "dim" )],
                 "ERROR"  : [True ,  False,   ("red",     "dim" )],
                 "FAIL"   : [True ,  True,    ("red",     "bold")],
                 "PASS"   : [True ,  True,    ("green",   "bold")],
                 "ABORT"  : [True ,  True,    ("red",     "bold")],
                  #TO BE REMOVED
                 "CYCLE"  : [True ,  True,    ("white",   "dim" )]}

    _threads   = []
    
    class _ThreadEntry(object):
        """
        """
        def __init__(self, logName, created, batchId, uniqueId):
            """
            """
            self.logName  = logName
            self.created  = created
            self.batchId  = batchId
            self.uniqueId = uniqueId
    
    def __init__(self, filename="", batchId=""):
        """System log object constructor."""
        self.terminal = TerminalControl()
        self._status = Status.status()

        self.logName  = "log-"+filename+'.txt'
        self.batchId  = batchId
        self.uniqueId = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        self.created  = ""
        
        if filename and batchId:
            self.bind()

    def setUniqueID(self, uuid):
        """
        """
        threadName = threading.currentThread()#.getName()
        self.uniqueId = uuid
        for i, (name, entry) in enumerate(SystemLog._threads):
            if threadName is name:
                entry.uniqueId = self.uniqueId
                SystemLog._threads[i] = (name, entry)
                break

    def setCreated(self, created):
        """
        """
        threadName = threading.currentThread()#.getName()
        self.created = created
        for i, (name, entry) in enumerate(SystemLog._threads):
            if threadName is name:
                entry.created = self.created
                SystemLog._threads[i] = (name, entry)
                break

    def bind(self):        
        """
        """
        #Get current number of bound threads
        numThreads = len(SystemLog._threads)
        
        #Get name of currently executing thread and add to list
        threadName = threading.currentThread()#.getName()
        entry = self._ThreadEntry(self.logName, self.created, self.batchId, self.uniqueId)
        SystemLog._threads.append((threadName, entry))

        #Search for previously bound job id for the current thread
        for i in range(numThreads):
            name, entry = SystemLog._threads[i]
            if threadName is name:
                #Unbind previously bound job id for this thread
                SystemLog._threads.pop(i)
                break
        
    def unbind(self):
        """
        """
        #Get name of currently executing thread
        threadName = threading.currentThread()#.getName()

        #Search for current thread in bound job id list
        for i, (name, entry) in enumerate(SystemLog._threads):
            if threadName is name:
                SystemLog._threads.pop(i)
                break
        
        #No other threads bound to this job id, so remove it from dictionary
        #status.__status.pop(boundJobId,'')
        
    def __logMessage(self, tag, message):
        """
        Outputs given message to the system log file if enabled.
        Displays given message on the screen if enabled.
        
        @type      tag: string
        @param     tag: The tag to be used when logging the given message
        @type  message: string
        @param message: The message to be logged
        """
        threadName = threading.currentThread()#.getName()
          
        for i, (thread_name, entry) in enumerate(SystemLog._threads):
            if threadName is thread_name:
                self.logName  = entry.logName
                self.created  = entry.created
                self.batchId  = entry.batchId
                self.uniqueId = entry.uniqueId
                break

        today = str(datetime.today().strftime("%Y/%m/%d"))
        if today != self.created:
            # create a new log for today
            self.created = today
            self.setCreated(self.created)
            self.bind()
            pathName = "./logs/"+self.created+"/"+self.batchId
            try:
                # create directory to store log files
                os.makedirs(pathName)
            except:
                pass
        else:
            pathName = "./logs/"+self.created+"/"+self.batchId
                
        logMessage = "<" + tag + ">" + " "*(8-len(tag)) + '[' + strftime("%d.%m.%y %H:%M:%S") + '] ' + message

        if (tag == "STATUS"):
            self._status.set(message)
            
        else:
            try:
                self.logFile = file(pathName+'/'+self.logName, 'a')
            except:
                print 'Failed to open logfile', self.logName
                return
            if self.logFile:
                # log against the uniqueID, but don't add to message as we don't need it printed on the screen
                try:
                    self.logFile.write('['+self.uniqueId + '] ' + logMessage + "\n")
                    self.logFile.flush()
                except:
                    print 'Error writing to logfile', self.logName

        colour, style = SystemLog._tagTable[tag][2]
        self.terminal.cprintln(logMessage, colour, style)
 
    def closeLog(self):
        """Close the active log file"""
        if self.logFile:
            self.unbind()
            self.logFile.close()

    def cycle(self, message):
        """
        Log CYCLE message.
        Used for start of test cycle which may include multiple tests
        
        @type  message: string
        @param message: The message to be output to the log
        """
        #print "CYCLE TAG HAS BEEN REMOVED"
        self.__logMessage("CYCLE", message)

    def test(self, message):
        """
        Log TEST message.
        Used for start of test
        
        @type  message: string
        @param message: The message to be output to the log
        """
        self.__logMessage("TEST", message)
    
    def iter(self, message):
        """
        Log ITERATION message.
        Used for start of test iteration
        
        @type  message: string
        @param message: The message to be output to the log
        """
        print "ITER TAG HAS BEEN REMOVED"
        #self.__logMessage("ITER", message)

    def info(self, message):
        """
        Log INFORMATION message.
        Used to output informational content to the log
        
        @type  message: string
        @param message: The message to be output to the log
        """
        self.__logMessage("INFO", message)

    def status(self, message):
        """
        Log INFORMATION message.
        Used to output informational content to the log
        
        @type  message: string
        @param message: The message to be output to the log
        """
        self.__logMessage("STATUS", message)

    def swver(self, message):
        """
        Log SOFTWARE VERSION UNDER TEST message.
        Used to output the software version being tested to the log
        
        @type  message: string
        @param message: The message to be output to the log
        """
        self.__logMessage("SWVER", message)        
    
    def config(self, message):
        """
        Log CONFIGURATION message.
        Used to indicate radio terminal configuration
        
        @type  message: string
        @param message: The message to be output to the log
        """
        self.__logMessage("CONFIG", message)

    def measure(self, message, value):
        """
        Log MEASUREMENT message.
        Used to record a measurement in the log
        
        @type  message: string
        @param message: The message to be output to the log
        @type    value: string, or numeric that is compatible with str() function
        @param   value: The measured value to be recorded in the log
        """
        message = message + ' [' + str(value) + ']'
        #self.__logMessage("MEASURE", message)
    
    def warning(self, message):
        """
        Log WARNING message.
        Used to indicate a warning situation encountered during test
        
        @type  message: string
        @param message: The message to be output to the log
        """
        self.__logMessage("WARNING", message)
    
    def alert(self, message):
        """
        Log ALERT message.
        Used to output informational content to the log
        
        @type  message: string
        @param message: The message to be output to the log
        """
        self.__logMessage("ALERT", message)

    def error(self, message):
        """
        Log ERROR message.
        Used to indicate an error encountered during test
        
        @type  message: string
        @param message: The message to be output to the log
        """
        self.__logMessage("ERROR", message)

    def reason(self, message):
        """
        Log REASON message
        
        @type  message: string
        @param message: The message to be output to the log
        """
        print "REASON TAG HAS BEEN REMOVED"
        #self.__logMessage("REASON", message)
        
    def ok(self, message):
        """
        Log PASS message.
        Used to indicate that a test has passes successfully
        
        @type  message: string
        @param message: The message to be output to the log
        """
        self.__logMessage("PASS", message)
    
    def fail(self, message):
        """
        Log FAILURE message.
        Used to indicate that a test has failed
        
        @type  message: string
        @param message: The message to be output to the log
        """
        self.__logMessage("FAIL", message)

    def append(self, message):
        """
        Append message to log.
        Used to continue output to the log file using the last specified message type.
        <Tag> and [Date/Time] are not output for appended log entries.
        
        @type  message: string
        @param message: The message to be output to the log
        """
        print "APPEND TAG HAS BEEN REMOVED"
        #self.__logMessage("APPEND", message)

    def abort(self, message):
        """
        Append message to log.
        Used to continue output to the log file using the last specified message type.
        <Tag> and [Date/Time] are not output for appended log entries.
        
        @type  message: string
        @param message: The message to be output to the log
        """
        self.__logMessage("ABORT", message)

    def traffic(self, message):
        """
        Log the traffic type (capacity/modulation) parameters to the log
        Used to indicate radio terminal configuration
        
        @type  message: string
        @param message: The message to be output to the log
        """
        self.__logMessage("TRAFFIC", message)
#
# Global Log
#
Log = SystemLog()

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#

