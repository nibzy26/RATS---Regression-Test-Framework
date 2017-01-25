#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Helper/ftp.py,

"""
FTP helper functions
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)
__revision__  = '$Header: /usr/local/cvsroot/stratex/rats/Helper/ftp.py

from   ftplib import FTP
import StringIO
import re
from Helper  import ftpd

def ftpConnect(ftpServer, user=None, pw=None, port=21):
    """
    connect to the specified FTP server, if no user/pw supplied then
    anonoymous login is used.

    @type  ftpServer   : string
    @param ftpServer   : The hostname / ipaddress of the ftpServer
    @type  user        : string
    @param user        : ftp server username
    @type  pw          : string
    @param pw          : ftp server password

    @rtype:  ftp session
    @return: connected ftp session 
    """
    retry = 0
    while 1:
        try:
            if user != None and pw != None:
                # if username/password supplied then use it
                ftp = FTP()
                ftp.connect(ftpServer, port)
                ftp.login( user, pw )
            else:
                # anoymous login, no retry logic here
                ftp = FTP()
                ftp.connect(ftpServer, port)
                ftp.login()
                
            return ftp
        except:
            # (TODO) except on ftperrors only
            retry = retry + 1
            if retry == 5:
                raise
            
    # should never get here
    return None


def uploadLines(ftpServer, user, pw, ftpDirectory, filename, fptr, port=21):
    """
    JHY to add comments here please

    @type  ftpServer   : string
    @param ftpServer   : The hostname / ipaddress of the ftpServer
    @type  user        : string or none
    @param user        : ftp server username
    @type  pw          : string or none
    @param pw          : ftp server password
    @type  ftpDirecroty: string
    @param ftpDirectory: The directory on the ftp server to download the file from
    @type  filename    : string
    @param filename    : The name of the file to download
    @type  fptr        : file descriptor
    @param fptr        : file descriptor of file to upload?
    """
    ftp = ftpConnect(ftpServer, user, pw, port)

    if ftp != None:
        ftp.cwd(ftpDirectory)
        
        ftp.storlines("STOR " + filename, fptr)
        
        ftp.quit()

        
def downloadLines(ftpServer, user, pw, ftpDirectory, filename, port=21):
    """
    Download a file from the ftp server specified and return the file as
    an array of bytes


    @type  ftpServer   : string
    @param ftpServer   : The hostname / ipaddress of the ftpServer
    @type  user        : string or none
    @param user        : ftp server username
    @type  pw          : string or none
    @param pw          : ftp server password
    @type  ftpDirecroty: string
    @param ftpDirectory: The directory on the ftp server to download the file from
    @type  filename    : string
    @param filename    : The name of the file to download
    
    @rtype:  array of bytes
    @return: an array of bytes containing the file data of the downloaded file
    """
    class ftpDownloader(object):
        """
        ftpDownloader : sub object to handle a single ftp download session
        """
        def __init__(self):
            """
            initalise ftp downloader
            """
            self.fileData = ""  # used to store filedata from ftp download

        def ftpHandleDownload( self,block ):
            """ callback to handle ftp transfer """
            self.fileData += block


    # create a downloader to handle the download, this makes this function thread safe    
    ftpd = ftpDownloader()
        
    # Attempt to connect to the ftp server and download the requested file
    try:
        ftp = ftpConnect(ftpServer, user, pw, port)
        
        ftp.cwd(ftpDirectory)

        # flush buffer used to capture ftp download
        ftpd.fileData = ""

        # download file from ftp server place in self.fileData               
        ftp.retrbinary('RETR '+filename, ftpd.ftpHandleDownload) 
        ftp.quit()

        return ftpd.fileData
        
    except:
        raise

    return None


def download(ftpServer, ftpDirectory, filename, port=21):
    """
    Download a file from the ftp server specified and return the file as
    an array of bytes


    @type  ftpServer   : string
    @param ftpServer   : The hostname / ipaddress of the ftpServer
    @type  ftpDirecroty: string
    @param ftpDirectory: The directory on the ftp server to download the file from
    @type  filename    : string
    @param filename    : The name of the file to download
    
    @rtype:  array of bytes
    @return: an array of bytes containing the file data of the downloaded file
    """
    if ftpServer == None:
         ftpServer = ftpd.getFtpServerAddress()
         
    return downloadLines(ftpServer, None, None, ftpDirectory, filename, port)
      
        
def getPortalVersion( ftpDirectory, versionXML=None ):
    """
    Download a specified version.xml file from the ftp server, uncompress it and return portalVersion

    @type  ftpDirecroty: string
    @param ftpDirectory: The directory on the ftp server to download the file from
    
    @rtype:  list
    @return: returns a list the first entry containing the portal version
    """
    
    from file import gunzipData as FileGunzipData

    ftpServer = ftpd.getFtpServerAddress()
        
    # connect to ftp server and generate a list of files        
    try:    
        ftp = FTP()
        ftp.connect(ftpServer, 5000)
        ftp.login()
        ftp.cwd(ftpDirectory)
        fileList = ftp.nlst()    
        ftp.quit()

    except:
        raise
        
    for fileName in fileList:
        # parse fileList search for version.xml file
        if versionXML != None:
            fileVersion = re.findall(versionXML, fileName)
        else:
            fileVersion = re.findall('idu_xxx_version.xml-(\S+).gz', fileName)
            
        # if the file matches our search criteria, assume this is the version.xml file
        # download the file from the ftp server and decompress it into versionData
        if fileVersion:
            # download and extract version
            if versionXML != None:
                fileData = download( ftpServer, ftpDirectory, fileVersion[0], port=5000)
            else:
                fileData = download( ftpServer, ftpDirectory, 'idu_xxx_version.xml-'+str(fileVersion[0])+'.gz', port=5000)
                
            if fileData:    
                versionData = FileGunzipData( fileData )
                if versionData:
                    # scan the versionData for the portal version number
                    return re.findall("version number='(\S+)'" , versionData )
                
                print 'gunzipError'
                return None
            
            else:
                print 'ftp error'
                return None                    
        
    return None


if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"



            
                    