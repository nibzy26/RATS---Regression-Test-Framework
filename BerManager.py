#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Traffic/BerManager.py,

"""
BER Tester Manager
Provides interface to BER tester functions for traffic control and checking.
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

from eBerType import eBerType
import BerTester
from System import Config

def initBerTesters():
    manager = BerManager()

    # handle error here
    berconfig = Config.loadConfig('ber.conf')

    if not berconfig:
        return
    
    for berID in berconfig:
        address = berconfig[berID]['address'] 
        type    = eval('eBerType.'+berconfig[berID]['type'].upper())

        try:
            ber = manager.add_Ber(address, type, address, 2)
            print 'added ber', address, berconfig[berID]['type']
        except:
            print 'failed to add ber', address
            continue
        
        # parse connections
        for i in range(1,21):
            try:
                channel = berconfig[berID]['channel'+str(i)].split(',')
            except:
                continue
            
            ber.add_connection(channel[0].strip(), int(channel[1].strip()),int(channel[2].strip()), i)
            print 'added conntection', channel[0].strip(), channel[1].strip(), channel[2].strip(), i                                                                          

class BerManager(object):

    ber_list = []

    def __init__(self):
        #read config from file
        pass

    def add_Ber(self, berId, berType, *args):
        """
        """
        from Ber_Loopback import Ber_Loopback
        from Ber_IDU300_20x import Ber_IDU300_20x
        from Ber_Manual import Ber_Manual
        from Ber_IDU300_20x_BER import Ber_IDU300_20x_BER
    
        for ber in BerManager.ber_list:
            if ber.id == berId:
                print "Ber tested already exists with id:", berId
                raise

        if berType == eBerType.BER_TYPE_PHYSICAL_LOOPBACK:
            ber = Ber_Loopback(berId, *args)
        elif berType == eBerType.BER_TYPE_IDU_300_20X:
            ber = Ber_IDU300_20x(berId, *args)
        elif berType == eBerType.BER_TYPE_IDU_300_20X_BER:
            ber = Ber_IDU300_20x_BER(berId, *args)
        elif berType == eBerType.BER_TYPE_MANUAL:
            ber = Ber_Manual(berId, *args)
        else:
            print "Unsupporter ber tester type:", berType
            raise BerTester.BerFailError
        BerManager.ber_list.append(ber)
        return ber

    def get_Ber(self, terminal, slot, trib):
        """
        """
        for ber in BerManager.ber_list:
            connection = ber.get_connection(terminal, slot, trib)
            if connection:
                return ber
        return None

    def ber_function(self, function, terminal, slot, trib, *args):
        """
        """
        result = 0
        ber = self.get_Ber(terminal, slot, trib)
        #print 'using ber :::', terminal,  ber
        try:
            if not ber:
                raise BerTester.BerNotAvailableError
            function = "ber." + function
            result = eval(function)(terminal, slot, trib, *args)

        except BerTester.BerNotAvailableError:
            #Warning message: No BER tester available for specified tributary
            print "BER TESTER NOT AVAILABLE FOR SPECIFIED TRIB"
            #result = -1

        except BerTester.BerNotSupportedError:
            #Warning message: BER tester does not support this function
            print "BER TESTER DOES NOT SUPORT THIS FUNCTION",function,"for", terminal,slot,trib
            #pass
            #result = -2

        except BerTester.BerFailError:
            #Error message: BER tester failure
            result = 1
            raise

        return result



if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#

#

#
