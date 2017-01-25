#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Helper/http.py,

"""
perform http operations on the terminal
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import httplib
import StringIO, re

def download(node, filename):
    """
    Connect to the provided terminal via its http interface and download the logread file
    """
    # connect to http server on radio and download logread
    try:
        conn = httplib.HTTPConnection(node.address)
        conn.request("GET", filename)
        res = conn.getresponse()
    except:
        # failed to retrieve log from terminal
        return None
    
    if res.status != 200 and res.reason != "OK":
        conn.close()
        # failed to download file
        return None

    data = res.read()
    conn.close()
    
    return data


def retrieveCfg(node):
    """
    retrieve the cfg-active from the node requested
    """
    data = download(node, '/cfg-active')
    if data:
        return StringIO.StringIO(data)

    return None

def retrieveLog(node):
    """
    retrieve the syslog from the node requests, and its odus (TODO TEST THIS)
    """
    data = download(node, '/logread')
    if data:
        return StringIO.StringIO(data)

    return None


def retrieveLogAll(node):
    """
    retrieve the syslog from the node requests, and its odus (TODO TEST THIS)
    """
    data = download(node, '/logread_all')
    if data:
        return StringIO.StringIO(data)

    return None


def retrieveVersionXML(node):
    """
    retrieve the version.xml file from the terminal
    """
    return download(node, '/version.xml')


def retrieveSysInfo(node):
    """
    retrieve the Sys Info from the provided terminal
    """
    data = download(node, '/syslst')
    if data:
        return StringIO.StringIO(data)

    return None


def retrieveAsBuiltReport(node):
    """
    retrieve the As Built Report from the provided terminal
    """
    data = download(node, '/AsBuiltReport.csv')
    if data:
        return StringIO.StringIO(data)

    return None


def radioGetPortalVersion( node ):
    """
    get Portal version from Radio
    """
    versionData = retrieveVersionXML(node)
        
    if versionData:
        # scan the versionData for the portal version number
        return re.findall("version number='(\S+)'" , versionData )
        
    return None


if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

