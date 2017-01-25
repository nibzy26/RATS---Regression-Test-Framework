#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Network/NetworkManager.py,

"""
Network Management Module
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import Components, types, cPickle, Interface, time
from Enum.eHwType import eHwType
from Enum.eProtType import eProtType
from Enum.eTestStatus import eTestStatus
from Snmp.Session import ContextSession
from Snmp.SnmpManager import SnmpManager

class NetworkManager(object):
    """
    """
    
    #def __init__(self):
    """
    """
        #read network info from file
    terminals = {}
    links     = {}
    networks  = {}

    def __init__(self):
        #If Network information has not yet been populated, read it from disk
        if not (NetworkManager.terminals or NetworkManager.links or NetworkManager.networks):
            self.loadNetworkInfo()

    def loadNetworkInfo(self, filename = "./Network/Config/network.dat"):
        """
        """
        result = True
        data_list = None
        netFile = None
        try:
            netFile = open(filename, 'rb')
            data_list = cPickle.load(netFile)
            NetworkManager.terminals, NetworkManager.links, NetworkManager.networks = data_list
        except:
            result = False
        if netFile:
            netFile.close()
        return result
    
    def saveNetworkInfo(self, filename = "./Network/Config/network.dat"):
        """
        """
        result = True
        data_list = [NetworkManager.terminals, NetworkManager.links, NetworkManager.networks]
        netFile = None
        #try:
        netFile = open(filename, 'wb')
        cPickle.dump(data_list, netFile, cPickle.HIGHEST_PROTOCOL)
        #except:
        #    print "error saving network info"
        #    result = False
        if netFile:
            netFile.close()
        return result

    def lockNetwork(self, netId):
        network = NetworkManager.networks.get(netId)
        if not network:
            print 'network not found', netId
            raise
        while NetworkManager.networks[netId].status != eTestStatus.UNUSED:
            time.sleep(1)
        NetworkManager.networks[netId].status = eTestStatus.RUNNING
        
    def unlockNetwork(self, netId):
        network = NetworkManager.networks.get(netId)
        if not network:
            print 'network not found', netId
            raise
        NetworkManager.networks[netId].status = eTestStatus.UNUSED

    def createInterface(self, netId=0, linkId=0, terminalId=0):
        """
        """
        class NetInterface(object):
            pass

        _manager = SnmpManager()

        #Lock network        
        self.lockNetwork(netId)

        network  = None             
        link     = None
        terminal = None
        
        #Check network exists with specified id
        network = NetworkManager.networks.get(netId)
        if not network:
            # Network not found with specified id
            print 'network not found', netId
            return None

        #Check link exists with specified id (ant terminal id if specified)
        if linkId:
            if linkId in network.links:
                link = NetworkManager.links.get(linkId)
                if link:
                    if terminalId and not terminalId in link.terminals:
                        link = None
        else:
            if terminalId:
                for linkId in network.links:
                    link = NetworkManager.links.get(linkId)
                    if link:
                        if terminalId in link.terminals:
                            break
                    else:
                        link = None
            else:
                link = NetworkManager.links.get(network.links[0])

        if not link:
            print 'link not found'
            #Link not found
            #a) with specified id OR
            #b) containing specified terminal id
            return None

        #Create interface objects
        if link.protected > eProtType.PROT_TYPE_NN:
            #Protected Link
            primary, secondary = link.pointA
            primaryId, primaryslot = primary
            secondaryId, secondaryslot = secondary
            local                   = Interface.Interface(primaryId) #ContextSession(ip)
            local.protected         = link.protected
            local.racSlot           = primaryslot
            local.dacSlot           = 2
            local.primary           = Interface.Interface(primaryId) #ContextSession(ip)
            local.primary.racSlot   = primaryslot
            local.primary.dacSlot   = 2
            local.secondary         = Interface.Interface(secondaryId) #ContextSession(ip)
            local.secondary.racSlot = secondaryslot
            local.secondary.dacSlot = 2

            primary, secondary = link.pointB
            primaryId, primaryslot = primary
            secondaryId, secondaryslot = secondary
            remote                   = Interface.Interface(primaryId) #ContextSession(ip)
            remote.protected         = link.protected
            remote.racSlot           = primaryslot
            remote.primary           = Interface.Interface(primaryId) #ContextSession(ip)
            remote.primary.racSlot   = primaryslot
            remote.primary.dacSlot   = 2
            remote.secondary         = Interface.Interface(secondaryId) #ContextSession(ip)
            remote.secondary.racSlot = secondaryslot
            remote.secondary.dacSlot = 2

        else:
            #print 'non protected link'
            #Non Protected Link
            terminalId, slot = link.pointA
            local            = Interface.Interface(terminalId) #ContextSession(ip)
            local.protected  = link.protected
            local.racSlot    = slot
            local.primary    = None
            local.secondary  = None
            
            terminalId, slot = link.pointB
            remote           = Interface.Interface(terminalId) #ContextSession(ip)
            remote.protected = link.protected
            remote.racSlot   = slot
            remote.primary   = None
            remote.secondary = None

            #--- debug ----
            #print 'local = ', local.address
            #print 'remote =', remote.address

        interface = NetInterface()
        interface.netId     = netId
        interface.linkId    = link.id
        interface.protected = link.protected
        interface.local     = local
        interface.remote    = remote
        return interface

    def _new_id(self, idList):
        """
        """
        id = 1
        while id in idList:
            id += 1
        return id

    def new_terminal(self):
        """
        """
        terminal = Components.RadioTerminal()
        terminal.id = self._new_id(NetworkManager.terminals.keys())
        print "Terminal id is " , terminal.id
        NetworkManager.terminals[terminal.id] = terminal
        return terminal

    def get_terminal(self, address):
        """
        """
        for terminal in NetworkManager.terminals.values():
            if terminal.address == address:
                return terminal
        return None

    def getTerminalByIp(self, networkId, address):
        """
        """
        for terminal_id in NetworkManager.networks[networkId].terminals:
            if NetworkManager.terminals[terminal_id].address == address:
                return NetworkManager.terminals[terminal_id]
        return None

    def remove_terminal(self, id):
        """
        """
        if NetworkManager.terminals.get(id):
            del NetworkManager.terminals[id]

    def new_link(self):
        """
        """
        link = Components.RadioLink()
        link.id = self._new_id(NetworkManager.links.keys())
        NetworkManager.links[link.id] = link
        return link

    def remove_link(self, id):
        """
        """
        if NetworkManager.links.get(id):
            del NetworkManager.links[id]

    def new_network(self):
        """
        """
        network = Components.RadioNetwork()
        print "NetworkManager.networks keys are ",NetworkManager.networks.keys()
        network.id = self._new_id(NetworkManager.networks.keys())
        print network.id
        NetworkManager.networks[network.id] = network
        return network

    def remove_network(self, id):
        """
        """
        if NetworkManager.networks.get(id):
            del NetworkManager.networks[id]

def _debug_terminal(terminal_id):
    terminal = NetworkManager.terminals[terminal_id]
    print "     TERMINAL:", terminal.id
    print "   IP Address:", terminal.address
    print "Hardware type:", terminal.hwType
    print "          HSC:", terminal.hsc
    print "Serial Number:", terminal.serial
    print "  Part Number:", terminal.part
    print "       Status:", eTestStatus[terminal.status]
    print

def _debug_link(link_id):
    link = NetworkManager.links[link_id]
    print "LINK:", link.id
    print "From:",
    x,y = link.pointA
    if type(x) == types.TupleType:
        a,b = x
        c,d = y
        print NetworkManager.terminals[a].address,"slot",b,"/",NetworkManager.terminals[c].address,"slot",d
    else:
        print NetworkManager.terminals[x].address,"slot",y
    print "  To:",
    x,y = link.pointB
    if type(x) == types.TupleType:
        a,b = x
        c,d = y
        print NetworkManager.terminals[a].address,"slot",b,"/",NetworkManager.terminals[c].address,"slot",d
    else:
        print NetworkManager.terminals[x].address,"slot",y
    print

def _debug_dump():
    for network in NetworkManager.networks.values():
        print "======================================================================="
        print "NETWORK:", network.id
        print "------------------------------------------------------------- Terminals"
        for terminal_id in network.terminals:
            _debug_terminal(terminal_id)
        print "----------------------------------------------------------------- Links"
        for link_id in network.links:
            _debug_link(link_id)

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"


#
#