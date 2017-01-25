#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Snmp/Translator.py,

"""
OID Translator base class module.

A Translator is used to convert a symbolic object name, such as protConfigPrimaryContext,
into an SNMP object ID (e.g. '1.3.6.1.4.1.2509.8.14.2.1.1.3').
Object Instances are not appended to the OID.
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

class TranslatorError(Exception):
    """Base class for exceptions in this module."""
    pass

class InvalidObjectNameError(TranslatorError):
    """Exception raised for error with specified object name."""
    pass

class InternalError(TranslatorError):
    """Exception raised for implementation-specific unresolvable errors."""
    pass


class Translator(object):
    """
    Abstract base class for Translator functionality.
    """
    def translate(self, object_name):
        """
        Translate the specified object name and instance to an OID and type.

        @type  directory: string
        @param directory: The directory containing the MIB files
        @rtype:  tuple(string, string)
        @return: Tuple indicating (dotted numerical object ID, Object's SNMP data type)
        """
        pass

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#
#
#
