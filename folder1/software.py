#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Helper/software.py,

"""
software functions
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import re, string, sys, time
from Modules import Timer
from Helper  import ftpd

#
# softwareLoader class, allows loading of software to a single terminal
#
class SoftwareLoader(object):
    
    def __init__(self, node, version, ftpServer, ftpUser, ftpPass, context="terminal"):
        # format IP address to match SnmpUDPAddress type 4 bytes IP + 2 bytes port number 
        #self.ftpServer       = self.convertIP(ftpServer)
        # force local FTP server
        self.ftpServer       = self.convertIP(ftpd.getFtpServerAddress())
        self.ftpUser         = ftpUser
        self.ftpPassword     = ftpPass
        self.version         = version
        self.downloadTimeout = 800
        self.activateTimeout = 800
        self.node = node
        self.community = context
        self.count = 0

        #print 'set community to ' + self.community
        
        #----------------------------------------------------------------------

    def convertIP(self, address):
        """ address in format aaa.bbb.ccc.ddd returns SnmpUDPAddress """
        
        if re.match('(\d+).(\d+).(\d+).(\d+)', address ):
            ip = re.findall('(\d+)',address)
            if len(ip) != 4:
                return 0

            port = 5000
            
            return chr(int(ip[0])) + chr(int(ip[1])) + chr(int(ip[2])) + chr(int(ip[3])) + chr( (port >> 8)& 0xFF) + chr(port & 0xFF)
        return 0
    

    def activate(self):
        """
        activate software
        """
        self.node.community = self.community
        self.skipOdu = 0
        try:
            unitType = self.node.get('mfgDetailsInfoUnitType', 1)

            if (string.find(unitType,'HP') > 0) or (string.find(unitType,'SP') > 0):
                #print 'skip ODU'
                self.skipOdu = 1
                return            
        except KeyboardInterrupt:
            raise
        except:
            raise
        
        if self.skipOdu == 1:
            return

        self.node.set('swLoadControl' , 0, 2 )         

    def abort(self):

        if self.skipOdu:
            return

        self.node.community = self.community
        
        # if not idle or activated ok
        try:
            self.node.set('swLoadControl', 0, 0 )
             # (TODO) perhaps wait here for terminal to return to idle, for now just wait 5 seconds
            time.sleep(5)
        except KeyboardInterrupt:
            raise
        except:
            raise #'failed to abort any existing software load'

       
    def load(self):
        """
        download software from ftp server into terminal
        """
        self.node.community = self.community   
        self.skipOdu = 0
        try:
            unitType = self.node.get('mfgDetailsInfoUnitType', 1)

            if (string.find(unitType,'HP') > 0) or (string.find(unitType,'SP') > 0):
                #print 'skip ODU'
                self.skipOdu = 1
                return            
        except KeyboardInterrupt:
            raise
        except:
            raise #'failed to retrieve mfgDetailsInfoUnitType'

        # abort any existing software loads            
        self.abort()

        # configure terminal for ftp software load                
        try:
            # disable software rollback
            self.node.set('swLoadRollbackDuration', 0, 0 )
            # disable delayed activation
            self.node.set('swLoadActivateWaitDuration', 0, 0)

            # setup terminal for FTP download            
            self.node.set('swLoadFile'           , 0, 'eclipse-' + self.version + '.bdf')
            self.node.set('swLoadServer'         , 0, self.ftpServer                    )
            self.node.set('swLoadServerDirectory', 0, 'eclipse-' + self.version         )
            self.node.set('swLoadUser'           , 0, self.ftpUser                      )
            self.node.set('swLoadPassword'       , 0, self.ftpPassword                  )
            self.node.set('swLoadControl'        , 0, 1                                 ) # 3 load and activate
            
        except:
            raise #'failed to set object required for ftp load'

        self.lastPercentage = 0

    #----------------------------------------------------------------------
    # wait for the software load to complete
    #----------------------------------------------------------------------
    def getLoadPercent(self):

        """                      abort(0),
                                 load(1),
                                 activate(2),
                                 loadAndActivate(3),
                                 rollback(4),
                                 forceLoad(5),
                                 forceActivation(6),
                                 idle(7),
                                 loadOk(8),
                                 activateOk(9),
                                 rollbackOk(10),
                                 loadWarning(11),
                                 activateWarning(12),
                                 compatibilityError(13),
                                 loadError(14),
                                 activateError(15),
                                 rollbackError(16),
                                 waitingToActivate(17)
        """

        self.node.community = self.community
        
        swLoadPercentage = 0
        swLoadControl = 0

        if self.skipOdu == 1:
            return 100

        try:
            swLoadPercentage = int(self.node.get('swLoadPercentage', 0, False))
            self.count = 0
        except KeyboardInterrupt:
            raise
        except:
            # count, if this occurs 25 times then raise exception
            self.count += 1
            if self.count >= 50:
                self.abort()
                raise
            
            swLoadPercentage = self.lastPercentage
                
        self.lastPercentage = swLoadPercentage
            
        try:
            swLoadControl    = int(self.node.get('swLoadControl', 0, False))
            self.count = 0
        except KeyboardInterrupt:
            raise
        except:
            # count, if this occurs 25 times then raise exception
            self.count += 1
            if self.count >= 50:
                self.abort()
                raise
            
            return swLoadPercentage

        # Aborted
        if swLoadControl == 0:
            raise "Software update aborted"
            return -1
        # loading 
        elif swLoadControl == 1:
            pass
        # Idle (perhaps aborted, but we missed change in state)
        elif swLoadControl == 7:
            raise "Software update aborted, idle"
            return -1
        # load warning
        elif swLoadControl == 11:
            #raise "Software load warning"
            #return -1
            pass
        # compatibility Error
        elif swLoadControl == 13:
            raise "Software compatibility Error"
            return -1
        # load error
        elif swLoadControl == 14:
            raise "Software load failed"
            return -1
        # Loaded ok, still waiting on activation
        elif swLoadControl == 8:
            return 100
        # waiting to activate
        elif swLoadControl == 17:
            return 100
        else:
            print '***** unknown swLoadControl == ', swLoadControl
            
        return swLoadPercentage         


    #----------------------------------------------------------------------
    # wait for the software load to complete
    #----------------------------------------------------------------------
    def getActivateState(self):

        self.node.community = self.community
        swLoadControl = 0

        if self.skipOdu == 1:
            return 1
        
        try:
            swLoadControl = int(self.node.get('swLoadControl', 0, False))
            #print swLoadControl
        except:
            #print "swLoadControl, failed to retrieve"
            return 0

        # Aborted
        if swLoadControl == 0:
            raise 'Software update aborted'
            return -1
        # Activating, still wait for reboot and activated ok result
        elif swLoadControl == 2:
            print 'Activating'
            return 0
        # Idle (perhaps aborted, but we missed change in state?)
        elif swLoadControl == 7:
            print 'Idle'
            #return -1
            #pass
            return 1
        elif swLoadControl == 15:
            raise 'Software activation error'
            return -1
        # Loaded ok, still waiting on activation
        elif swLoadControl == 8:
            print 'Loaded waiting on Activation'
            return 0
        # Activated ok
        elif swLoadControl == 9:
            print 'Activated ok'
            #progress.clear()
            return 1
        else:
            print self.node.address, ':', self.node.community, ':', swLoadControl

        return 0        



#------------------------------------------------------------------------------
# helper functions follow
#------------------------------------------------------------------------------
def loadLink( local, remote, version, ftpServer, ftpUser, ftpPassword ):
    """
    specify software to load and wait for it to complete
    """
    
    # setup software loaders
    swLoaders = []

    # (TODO) add entries for all attached ODUS
    swLoaders.append(SoftwareLoader(local,  version, ftpServer, ftpUser, ftpPassword, "odu1"))
    swLoaders.append(SoftwareLoader(remote, version, ftpServer, ftpUser, ftpPassword, "odu1"))
    swLoaders.append(SoftwareLoader(local,  version, ftpServer, ftpUser, ftpPassword, "terminal"))
    swLoaders.append(SoftwareLoader(remote, version, ftpServer, ftpUser, ftpPassword, "terminal"))

    for loader in swLoaders:
        loader.load()

    Timer.Wait("Giving time for software load to begin", 10)
    
    # wait for load
    progress = Timer.PeriodicWait( "Waiting for load...", 3600, 10)  # allow 1 hour for load.
    total = 0
    while total < (len(swLoaders) * 100):
        total = 0
        for loader in swLoaders:
            ret = loader.getLoadPercent()
            if ret == -1:
                return False
            else:
                total += ret

        #print 'total =', total, 'of', (len(swLoaders) * 100)
             
        progress.periodic()

        if progress.remaining == 0:
            #self.failTest('timeout during software load')
            print 'timeout'
            return False

    return True        
        

def activateLink( local, remote ):
    """
    activate loaded software on both ends of a link
    """
        
    # setup software loaders
    swLoaders = []

    # (TODO) add entries for all attached ODUS
    swLoaders.append(SoftwareLoader(local,  "", "", "", "", "odu1"))
    swLoaders.append(SoftwareLoader(remote, "", "", "", "", "odu1"))
    swLoaders.append(SoftwareLoader(local,  "", "", "", "", "terminal"))
    swLoaders.append(SoftwareLoader(remote, "", "", "", "", "terminal"))

    for loader in swLoaders:
        loader.activate()
    
    # wait for activate
    progress = Timer.PeriodicWait( "Waiting for activation...", 800, 10 )
    total = 0
    while total < len(swLoaders):
        total = 0
        
        for loader in swLoaders:
            total += loader.getActivateState()

        #print 'total = ', total, 'of', len(swLoaders)            

        progress.periodic()

        if progress.remaining == 0:
            # (TODO) check to see what software version is the active software
            # if this is the version we expect then pass?
            print 'timeout during activation'
            return False

    return True



def reset( node , timeout=500, ignoreAlarms=False, mode=1):
    """
    SoftReset, wait for terminal to boot up and any alarms to clear   
    """

    # set soft reset
    node.terminal.set('swManagerSoftReset', 1, mode)
          
    # wait until we can't retrieve the serial number
    progress = Timer.PeriodicWait("Waiting for restart...", 400, 10)
    while progress.remaining:
        try:
            swReset = node.terminal.get('swManagerSoftReset', 1, False )
        except KeyboardInterrupt:
            raise       
        except:
            break

        progress.periodic()
        
    if not progress.remaining:
        return False

    # timer just to make sure that we have restarted before waiting for boot
    Timer.Wait("Waiting for restart", 30)

    # wait for terminal to come back up        
    progress = Timer.PeriodicWait("Waiting for boot...", 400, 10)
    while progress.remaining:
        try:
            swReset = node.terminal.get('swManagerSoftReset', 1, False )
            if int(swReset) == 2:
                break
        except KeyboardInterrupt:
            raise       
        except:
            pass

        progress.periodic()

    if not progress.remaining:
        return False

    # wait for alarms to clear
    if ignoreAlarms:
        return True
    
    progress = Timer.PeriodicWait("waiting for alarms to clear", 300, 10)
    while progress.remaining:
        if linkActive( node ):
            return True

        progress.periodic()
            
    return False            


def linkActive(node):
    """
    check if a radio link between terminals is active
    """
    
    # if the active alarms match any of the following then we have a problem        
    link_alarms = ["demodulator not locked",
                    "remote communications failure",
                    "modulator not locked"]
        
    alarms = node.alarms.checkAll()

    for alarm in alarms:
        # alarm severity < 4 then could block traffic, need to test these
        if int(alarm[1]) < 4:
            #print 'severity < 4, assume link broken'
            return False

        # 
        #for link_alarm in link_alarms:
        #    if alarm[0] == link_alarm:
        #        return False

    return True


if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"
