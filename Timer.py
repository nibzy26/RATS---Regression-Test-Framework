#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Modules/Timer.py,

"""
Provides Timer functions for measuring elapsed time
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import time
from SysLog import SysLog

class Timer(object):
    """Timer object. Provides methods for measuring elapsed time."""
    
    def __init__(self, HighRes=False):
        """
        Initialises and starts timer, and selects resolution of clock source.
        
        @type  HighRes: boolean
        @param HighRes: If set to True, the high resolution clock source will be used.
                        Default value of False will use standard clock resolution.
        """
        if HighRes:
            self.clock = time.clock
        else:
            self.clock = time.time
        self.stop_time = 0.0
        self.start()

    def start(self):
        """Start timer. If timer is already running, the start time is updated"""
        self.running = True
        self.start_time = self.clock()

    def stop(self):
        """
        Stop timer, and return the elapsed time in seconds.

        @rtype:  float
        @return: Time elapsed in seconds (between calls to .start and .stop)
        """
        if self.running:
            self.stop_time = self.clock()
            self.running = False
        time_elapsed = self.stop_time - self.start_time
        return time_elapsed

    def elapsed(self):
        """
        Return the elapsed time in seconds, without stopping timer.

        @rtype:  float
        @return: Time elapsed between call to .start and NOW if timer is running,
                 Time elapsed between calls to .start and .stop if timer has already been stopped.
        """
        if self.running:
            stop_time = self.clock()
        else:
            stop_time = self.stop_time

        time_elapsed = stop_time - self.start_time
        return time_elapsed

class Wait(Timer):
    """
    Provides a delay timer. Suspends execution until the specified duration has elapsed.
    """
    def __init__(self, description="", delay=0):
        """
        Initialise and start timer
        Wait until specified delay period has expired
        """
        #status = Status.status()
        SysLog.Log.status(description)
        
        #print description
        Timer.__init__(self)
        while self.elapsed() < delay:
            time.sleep(1)

class PeriodicWait(Timer):
    """
    Periodic timer class
    Provides a delay timer with adjustable delay duration and period
    Calls to the periodic method allow the calling script to perform
    actions at regular intervals until the specified duration has elapsed.
    """
    def __init__(self, description="", delay=0.0, period=3.0):
        """
        Initialise and start timer
        """
        SysLog.Log.status(description)
        
        Timer.__init__(self)
        self.remaining = delay
        self._delay = delay
        self._period = period
        self._time = self.elapsed()
        
    def periodic(self):
        """
        Wait until calculated delay period has expired
        Delay calculated as the specified period minus the
        time elapsed since the last call to periodic.
        """
        elapsed = self.elapsed()
        self.remaining = self._delay - elapsed
        if self.remaining < 0:
            self.remaining = 0
        else:
            duration = self._period - (elapsed - self._time)
            self._time = elapsed
            if duration > 0:
                time.sleep(duration)

        # force sleep 500ms, allow time for task switch              
        time.sleep(0.50)

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#
# $Log
#
