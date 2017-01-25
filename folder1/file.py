#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Helper/file.py

"""
file functions
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import gzip
import StringIO

def gunzipData( fileData ):
    """
    gunzip a compressed stream and return resulting data
    """
    try:
        # convert fileData to a Stream and decompress it into versionData    
        compressedstream = StringIO.StringIO(fileData)
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        return gzipper.read()
    
    except:
        return None


if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"
    