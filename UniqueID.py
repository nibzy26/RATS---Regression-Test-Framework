#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Modules/UniqueID.py,

"""
Provides methods for generating unique idenifiers
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

"""
import time, random, md5, socket, struct

def Generate():
#    """
#    Generates a unique ID (32bit) : this is a non-standard compliant unique ID to be used in the RATS system
#    """
"""
    t = long( time.time() * 32L )
    r = long( random.random()* 32L )
    try:
        a = socket.gethostbyname(socket.gethostname())
        a = struct.unpack('L',socket.inet_aton(a))[0]
    except:
        # if we can't get a network address, just imagine one
        a = random.random()* 32L
        
    return md5.md5(str(t ^ r ^ int(a))).hexdigest()[:8]

"""

import uuid

def Generate():
    return str(uuid.uuid1())
        

#
# $Log :$
#