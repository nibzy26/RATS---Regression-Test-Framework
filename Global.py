#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/System/Global.py,

"""
Global objects
Retains references to globally shared objects
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

from Snmp import Session, SnmpWrapper, PyTranslator, PtiWrapper
from SysLog import SysLog

class Global(object):
    snmpTranslator = None
    snmpWrapper = None
    ptiWrapper = None
    systemLog = None
    berList = []
    terminalList = []
    linkList = []

def initGlobals():
    Global.snmpTranslator = PyTranslator.PyTranslator()
    Global.snmpWrapper = SnmpWrapper.SnmpWrapperPySnmp()
    Global.ptiWrapper = PtiWrapper.PtiWrapper()
    Global.systemLog = None
    Global.berList = []
    Global.terminalList = []
    Global.linkList = []

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#

#
#
