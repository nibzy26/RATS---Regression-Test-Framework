#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Helper/nms.py,

"""
nms functions
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

#--------------------------------------------------------------------------
# imports
#--------------------------------------------------------------------------
import time
import sys
import telnet
from   socket import *
from   Modules import Timer
from SysLog import SysLog

USER = "root\r"
PW = "i8tp\r"
ROUTE_CMD = "route\r"
PING_CMD = "ping -c 4 "
PASS = "0%"

TIME_OUT = 10

class nmsTest:
    """
    test for NMS connectivity between two terminals over the radio path
    """
    
    def __init__(self, ip, port):
        """
        initialise NMS test
        """
        self.connection = telnet.Telnet(ip, port, USER, PW)
        self.route = []
        self.loss = []
        
    # get route on nms
    def getRouteInfo(self):
        """
        using the linux 'route' command extract the route to use for NMS
        """
        self.connection.send(ROUTE_CMD)
        result = self.connection.expect("#", TIME_OUT).split()
        
        itemIndex = 0
        while itemIndex < len(result):
            if result[itemIndex] == "Iface":
                itemIndex = itemIndex + 1
                break
            itemIndex = itemIndex + 1
    
        while itemIndex < len(result):
            if result[itemIndex + 7] != "eth0":
                self.route.append(result[itemIndex])
                itemIndex = itemIndex + 8
            else:
                break
                
    # ping route info
    def pingRoute(self):
        """
        ping across the route to check for NMS traffic
        """
        for ip in self.route:
            cmd = PING_CMD + ip + "\r"
            
            self.connection.send(cmd)
            
            result = self.connection.expect("#", TIME_OUT).split()
            
            itemIndex = 0
            for item in result:
                if item == "packet":
                    self.loss.append(result[itemIndex-1])
                    break
                itemIndex = itemIndex + 1
                
    # disconnect telnet session
    def finish(self):
        self.connection.disconnect()


def __nms_check(node):
    """
    confirm nms on given interface
    """   
    status = "Pass"

    try:
        interface = nmsTest(node.address, 23)
    except:
        status = "Fail"
        return status

    interface.getRouteInfo()
    interface.pingRoute()

    print 'NMS interface.loss = ', interface.loss
    
    if len(interface.loss) == 0:
        SysLog.Log.info("Route: " + str(interface.route) + " failed to retrieve result")
        status = "Fail"
    else:
        nms = 1
        for loss in interface.loss:
            if loss != "0%":
                SysLog.Log.info("Route: " + str(interface.route) + "     Loss: " + str(interface.loss))
                status = "Fail"
                #self.errorTest("Nms" + str(nms) + " lost")
                nms = nms + 1

    interface.finish()
    
    return status

#------------------------------------------------------------------------------
# helper functions follow
#------------------------------------------------------------------------------
def check(node):
    """
    confirm nms on given interface, if the initial test fails wait for 2 minutes before retrying
    if the second check fails then return 'Fail' otherwise return 'Pass'
    """   
    if __nms_check(node) == 'Fail':
        # wait for 2 minutes
        SysLog.Log.warning('Initial NMS check failed. Retry in 2 minutes')
        Timer.Wait('Waiting for NMS to come up')

        return __nms_check(node)

    return 'Pass'


if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"
