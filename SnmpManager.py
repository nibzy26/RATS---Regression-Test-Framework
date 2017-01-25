#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Snmp/SnmpManager.py,

"""
BER Tester Manager
Provides interface to BER tester functions for traffic control and checking.
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import Session, SnmpWrapper, PyTranslator, PtiWrapper, OagWrapper

class SnmpManager(object):
    """
    """
    sessions = {}
    
    def __init__(self):
        self._oag_wrapper = OagWrapper.OagWrapper
        self._pti_wrapper = PtiWrapper.PtiWrapper
        self._snmp_wrapper = SnmpWrapper.SnmpWrapperPySnmp()
        self._translator = PyTranslator.PyTranslator()

    def create_session(self, address='', community='terminal', port=161):
        if address in SnmpManager.sessions:
            #print 'SESSION %s already exists using it' % address
            return SnmpManager.sessions[address]
        
        session = Session.ContextSession(address, community, 161, self._translator, self._snmp_wrapper, self._pti_wrapper, self._oag_wrapper)
        #add session to Sessions
        SnmpManager.sessions[address] = session
        
        return session
        
        