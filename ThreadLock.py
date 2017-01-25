#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/System/ThreadLock.py,

"""
Thread Lock Module
"""

__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

from time import sleep
import threading

class LockManager(object):
    locks = {}

    def lock(self, lockName):
        lockObj = LockManager.locks.get(lockName)
        if not lockObj:
            lockObj = ThreadLock(lockName)
        LockManager.locks[lockName] = lockObj
        lockObj.lock()

    def lockValue(self, lockName, value):
        lockObj = LockManager.locks.get(lockName)
        if not lockObj:
            lockObj = ThreadLockValue(lockName)
        LockManager.locks[lockName] = lockObj
        lockObj.lock(value)

    def unlock(self, lockName):
        lockObj = LockManager.locks.get(lockName)
        if lockObj:
            lockObj.unlock()
            if not lockObj._locked:
                del LockManager.locks[lockName]

    def unlockForce(self, lockName, threadName):
        lockObj = LockManager.locks.get(lockName)
        if lockObj:
            lockObj.unlock(threadName)
            if not lockObj._locked:
                del LockManager.locks[lockName]

    def unlockForceAll(self, threadName):
        for lockObj in LockManager.locks.values():
            lockObj.unlock(threadName)
            if not lockObj._locked:
                del LockManager.locks[threadName]

class ThreadLock(object):
    """
    Provides a resource locking mechanism for threaded execution
    """
    def __init__(self, name):
        self.name = name
        """
        Start in unlocked state with an empty queue
        """
        self._locked = "" #Contains name of thread which currently has the lock
        self._queue  = [] #List of threads waiting to acquire the lock

    def _getLock(self, threadName):
        """
        Try to acquire lock

        @type  threadName: string
        @param threadName: Name of the currently executing thread
        @rtype:  boolean
        @return: True if lock aquired successfully, False otherwise
        """
        if not self._locked:
            #Not locked
            self._locked = threadName
            return True

        if self._locked == threadName:
            #Lock acquired via the queue
            return True

        #Could not obtain lock
        return False    
        
    def lock(self):
        """
        Suspend thread execution until resource lock is acquired
        """
        #Get name of currently executing thread
        threadName = threading.currentThread().getName()

        #Wait until lock can be acquired, checking every second.
        if not self._getLock(threadName):
            self._queue.append(threadName)
            print self.name, threadName, "waiting for lock"
            while not self._getLock(threadName):
                sleep(1)
        print self.name, threadName, "locked"

    def unlock(self, force=""):
        """
        Unlock for the currently executing thread, or force unlock given a thread's name.

        @type  force: string
        @param force: An unlock may be forced by passing in the thread's name
                      Specifying "FORCE" will cause ALL locks to be cleared
                      including the current, and any waiting in the queue.
        """
        #Get thread name from specified or currently executing
        threadName = force or threading.currentThread().getName()
        #If thread currently has the lock, then release it.
        if self._locked == threadName:
            if self._queue:
                self._locked = self._queue.pop(0)
            else:
                self._locked = ""
            print self.name, "unlocked:", threadName

        #If thread is waiting in the queue, then remove it.
        elif threadName in self._queue:
            self._queue.remove(threadName)
            print self.name, "unlocked:", threadName

        #Overkill. Causes lock to be forcefully cleared for ALL threads.
        elif threadName == "FORCE":
            self._locked = ""
            self._queue  = []
            #print self.name, "unlocked: ALL"

class ThreadLockValue(object):
    """
    Provides a resource locking mechanism for threaded execution
    """
    def __init__(self, name):
        """
        Start in unlocked state with an empty queue
        """
        self.name = name
        self._lockValue = 0
        self._locked = [] #dict of threads with locked value

    def _getLock(self, threadName, value):
        """
        Try to acquire lock

        @type  threadName: string
        @param threadName: Name of the currently executing thread
        @rtype:  boolean
        @return: True if lock aquired successfully, False otherwise
        """
        if not self._locked:
            #Not locked
            self._locked.append(threadName)
            return True

        elif self._lockValue == value:
            if not threadName in self._locked:
                #Locked, but requested value is already set
                self._locked.append(threadName)
                return True

        elif threadName in self._locked:
            self._locked.remove(threadName)

        #Could not obtain lock
        return False

    def lock(self, value):
        """
        Suspend thread execution until resource lock is acquired
        """
        #Get name of currently executing thread
        threadName = threading.currentThread().getName()

        #Wait until lock can be acquired, checking every second.
        if not self._getLock(threadName, value):
            #print self.name, threadName, "waiting for lock"
            while not self._getLock(threadName, value):
                sleep(1)
        #print self.name, threadName, "locked"

    def unlock(self, force=""):
        """
        Unlock for the currently executing thread, or force unlock given a thread's name.

        @type  force: string
        @param force: An unlock may be forced by passing in the thread's name
                      Specifying "FORCE" will cause ALL locks to be cleared
        """
        #Get thread name from specified or currently executing
        threadName = force or threading.currentThread().getName()

        #If thread currently has the lock, then release it.
        if threadName in self._locked:
            self._locked.remove(threadName)
            #print self.name, "unlocked:", threadName

        #Overkill. Causes lock to be forcefully cleared for ALL threads.
        elif threadName == "FORCE":
            self._locked = []
            #print self.name, "unlocked: ALL"

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#
