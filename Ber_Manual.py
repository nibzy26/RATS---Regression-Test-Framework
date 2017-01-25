#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Traffic/Ber_Manual.py

"""
Physical loopback BER tester module
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

from eBerType import eBerType
from BerTester import BerTester

class Ber_Manual(BerTester):
    """
    Class for physical loopback interface
    """
    def __init__(self, id, berAddress, slot):
        """
        Physical loopback BER tester initialisation
        Calls inherited __init__ method.
        
        @type  id: integer
        @param id: Unique ID of ber tester.
        """
        BerTester.__init__(self)
        self.id = id
        self.berType = eBerType.BER_TYPE_MANUAL

    def check(self, ip, slot, trib):

        print '***** please confirm traffic passes without error *****'
                
        print 'TODO : add funky pop-up dialog for this'
        
        return 0
    
         
if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#

# updated to use new interface
#
# Revision 1.1  2006/12/12 00:21:03  rholben
# BER tester functions self contained under single manager module
#
#
