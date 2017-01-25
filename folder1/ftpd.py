#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Helper/ftpd.py,
"""

   Basic Python FTP server

 
   
   Description :

       This is a quick attempt at a pure python ftp server, when a client connects to the
       server a new thread is created to handle the ftp session. 

       currently the server supports the following commands :
   
        USER, PASS, QUIT, NOOP, SYST, PORT/EPRT, PWD/XPWD, CWD, MKD/XMKD, RMD/XRMD
        TYPE, LIST, RETR, PASV, CDUP, SIZE, DELE, MDTM, RNTO, RNFM

        (TODO)

        AUTH, ABOR, STOR

       ** fixed? **
       currently the server is setup to use all ports in the 35525-40000 range, this is
       not desired. (TODO) find out why socket.bind doesn't fail on a port that is already
       open, and then implement a method that uses bind to determine if we can use this
       port or not.

"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)
__revision__  = '$Header: /usr/local/cvsroot/stratex/rats/Helper/ftpd.py,v 1.4 2007/03/22 02:45:56 cdewbery Exp $'

#-----------------------------------------------------------------------------------
# imports
#-----------------------------------------------------------------------------------
import select
#import signal
import socket
import threading
import string
import os
from   stat import *
import time

#-----------------------------------------------------------------------------------
# ftp Client (thread)
#
#-----------------------------------------------------------------------------------
class ftpClient(threading.Thread):
    """
    """
    
    def __init__(self, sock, server):
        """
        create a new ftpClient thread to handle a single client connection
    
        @type  sock   : socket
        @param sock   : client socket
        @type  server : ftp server
        @param server : 
        """
        threading.Thread.__init__(self)
        self.sock       = sock
        self.datasock   = None
        self.dataport   = 0
        self.passive    = False
        self.cwd        = server.homedir
        self.home       = server.homedir
        self.server     = server
        self.type       = 1            # ascii mode
        self.terminated = False
        self.rnfr       = None
                
    def send_reply(self, code, str ):
        """
        send response packet

        @type  code   : string
        @param code   : response code
        @type  str    : string
        @param str    : message to send
    
        """
        message = "%3d %s\r\n" % (int(code), str)
        try:
            self.sock.send(message)
        except:
            if self.server.debug:       
                print 'FTP : failed to send response'

        if self.server.debug:            
            print 'FTP >> ', message.strip()
        
    def get_cmd(self):
        """
        wait for a command
        """
        while not self.terminated:
            # use select
            r, w, x = [self.sock], [], []
            r, w, x = select.select(r, w, x, 1)
            if r:
                try:
                    c = self.sock.recv(1024)
                    return string.split(c, None, 2)
                except:
                    return None

    def create_datasock(self):
        """
        create ftp data tunnel
        """
        
        if not self.datasock:
            # no pasv or port command recieved
            self.send_reply( 500, 'no PASV/PORT specified')
            return None
        
        if self.passive:

            r, w, x = [self.datasock], [], []
            r, w, x = select.select(r, w, x, 10)
            if r:
                try:
                    (clientdata, address ) = self.datasock.accept()
                except:
                    if self.server.debug:       
                        print 'FTP : client data connection failed'
                    return None
            else:
                if self.server.debug:       
                    print 'FTP : timeout'
                self.send_reply( 500, 'hello, are you going to connect or not?' )
                return None
            
        else:
            self.datasock.connect((self.clientaddress, self.clientport))
            clientdata = self.datasock

        return clientdata


    def doDele( self, arg ):
        """
        set the rename from file
        """
        if arg[0] != '/':     
            arg = os.path.normpath(self.cwd + '/' + arg)
        else:
            arg = os.path.normpath(self.home + '/' + arg)

        try:
            os.remove( arg )
            self.send_reply( 200, 'file deleted')
        except:       
            self.send_reply( 500, 'could not delete' )
            
        
    def doRnfr( self, arg ):
        """
        set the rename from file
        """
        if arg[0] != '/':     
            self.rnfr = os.path.normpath(self.cwd + '/' + arg)
        else:
            self.rnfr = os.path.normpath(self.home + '/' + arg)

        self.send_reply( 350, 'ok' )

    def doRnto( self, arg ):
        """
        rename the rename from file to the file supplied
        """
        if not self.rnfr:
            self.send_reply( 500, 'RNFR was not called')
            return

        if arg[0] != '/':     
            filename = os.path.normpath(self.cwd + '/' + arg)
        else:
            filename = os.path.normpath(self.home + '/' + arg)
            
        try:
            os.rename( self.rnfr, filename )
        except:
            self.send_reply( 500, 'rename failed')
            return
        
        self.send_reply( 250, 'renamed ok')

        
    def doUser( self, username ):
        """
        handle user login
        """
        self.send_reply( 230, "Anonymous user logged in." )


    def doPassword( self, password ):
        """
        handler password
        """
        self.send_reply( 230, "Anonymous user logged in." )


    def doPort( self, arg ):
        """
        active mode, server will connect to client port during RETR and LIST
        """
        if self.datasock:
            self.datasock.close()
            
        splitarg = arg.split(',')
        self.clientaddress = splitarg[0] + '.' + splitarg[1] + '.' + splitarg[2] + '.' + splitarg[3]
        self.clientport    = ((int(splitarg[4]) & 0xFF) << 8) | (int(splitarg[5]) & 0xFF)

        # create a new stream socket for the data stream
        self.datasock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        # allow reuse of socket
        self.datasock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # passive mode off        
        self.passive = False

        self.send_reply( 200, "PORT command successful" )


    def doPwd( self ):
        """
        print working directory
        """
        if self.cwd != self.home:
            self.send_reply( 257, '"' + self.cwd + '" is the current directory')
        else:
            self.send_reply( 257, '"/" is the current directory') 


    def doCwd( self, arg ):
        """
        change working directory
        """
        if not arg:
            arg = self.home # '/' # change to home?
            self.cwd = self.home
            self.send_reply( 250, 'Change to '+str('/') )
            return
        
        else:
            if arg == '/' or arg == self.home:
                arg = self.home
                self.cwd = self.home
                self.send_reply( 250, 'Change to '+str('/'))
                return
        
        # if the path starts with / then use full path name, otherwise prefix with cwd            
        if arg[0] != '/':     
            dir = os.path.normpath(self.cwd + '/' + arg)
        else:
            dir = os.path.normpath(self.home + '/' + arg)

        # make sure we can't cwd outside home dir
        if self.cwd == self.home:
            if arg.startswith('..') or arg.startswith('/..'):
                self.send_reply( 500, 'no access, need to find code for this')
                return
                    
        if os.path.exists( dir ):
            self.cwd = dir
            self.send_reply( 250, 'Change to '+str(arg) )
        else:
            self.send_reply( 530, 'cannot change to directory ' + str(arg))     


    def doQuit( self ):
        """
        quit session, terminate
        """
        self.terminated = True
        self.send_reply( 221, 'Good Bye' )

    def doNoop( self ):
        """
        No op : no operation, checks server active
        """
        self.send_reply( 200, 'NOOP command successful' )
        
    def doSyst( self ):
        """
        return system type
        """
        self.send_reply( 215, 'UNIX Type : L8' )

    def doMkd( self, arg ):
        """
        make directory
        """
        if not arg:
            self.send_reply( 550, 'no directory')
            return

        if arg[0] != '/':     
            arg = os.path.normpath(self.cwd + '/' + arg)
        else:
            arg = os.path.normpath(self.home + '/' + arg)
            
        try:
            os.mkdir(arg)
        except:
            self.send_reply( 550, 'cannot make directory ' + str(arg))
            return
        
        self.send_reply( 257, 'created directory '+str(arg))

    def doRmd( self, arg ):
        """
        remove a directory
        """

        if not arg:
            self.send_reply( 550, 'no directory')
            return

        if arg[0] != '/':     
            arg = os.path.normpath(self.cwd + '/' + arg)
        else:
            arg = os.path.normpath(self.home + '/' + arg)
                     
        try:
            os.rmdir(arg)
        except:
            self.send_reply( 550, 'cannot remove directory ' + str(arg))
            return
        
        self.send_reply( 250, 'removed directory '+str(arg))

    def doAuth( self, arg ):
        """
        """
        self.send_reply( 502, "Security extensions not implemented" )
        

    def doType( self, arg ):
        """
        set data type, binary or ascii
        """
        # data type one of I,A,E, or L
        if arg.upper() == 'I':
            self.type = 2
            self.send_reply( 200, "Binary mode")
        elif arg.upper() == 'A':
            self.type = 1
            self.send_reply( 200, "ASCII mode")
        elif arg.upper() == 'L':
            # todo number of bits per byte here
            self.type = 2
            self.send_reply( 200, "Binary mode")
        else:
            self.send_reply( 504, "unknown type")


    def doList( self, arg ):
        """
        """        
        if not arg:
            dir =  os.path.normpath(self.cwd)
        else:
            # parse args here
            if arg[0] != '/':        
                dir = os.path.normpath(self.cwd + '/' + arg)
            else:
                dir = os.path.normpath(self.home + '/' + arg)
        
        # if arg is a directory
        try:
            status = os.stat( dir )
        except:
            self.send_reply( 500, 'cannot stat file' )
            return
                
        clientdata = self.create_datasock()
        if not clientdata:
            return
                    
        self.send_reply( 150, 'Opening ASCII mode data connection for file list')

        try:
                    
            if S_ISDIR(status[ST_MODE]):
                # directory mode
                for file in os.listdir(dir):
                    # get info on file
                    status = os.stat(dir+'/'+file)
                    if S_ISDIR(status[ST_MODE]):
                        mode = 'd'
                    elif S_ISREG(status[ST_MODE]):
                        mode = '-'
                    elif S_ISLNK(status[ST_MODE]):
                        mode = 'l'
                    else:
                        continue
                            
                    # format into ls mode
                    line = '%srw-r--r-- 1 %s %s %14s %s %s\r\n' % \
                           (mode, \
                            status[ST_UID], \
                            status[ST_GID], \
                            status[ST_SIZE], \
                            time.strftime('%b %d %H:%M', time.gmtime(status[ST_MTIME])), \
                            file)
                    
                    clientdata.send(line)
                            
            else:
                # file mode
                file = dir
                
                status = os.stat(file)
                # format into ls mode
                line = '-rw-r--r-- 1 %s %s %14s %s %s\r\n' % \
                       (status[ST_UID], \
                        status[ST_GID], \
                        status[ST_SIZE], \
                        time.strftime('%b %d %H:%M', time.gmtime(status[ST_MTIME])), \
                        file)
                
                clientdata.send(line)

            self.send_reply( 226, 'Transfer complete.')
                    
        except:
            self.send_reply( 500, 'Find error code for this')

        clientdata.close()

    def doCdup( self, arg ):
        """
        change the working directory to the parent of the current directory
        """
        self.doCwd('../')
        
        
    def doSize( self, arg ):
        """
        return the Size of the specified file
        """
        if arg[0] != '/':     
            arg = os.path.normpath(self.cwd + '/' + arg)
        else:
            arg = os.path.normpath(self.home + '/' + arg)

        if os.path.isfile( arg ):            
            try:
                size = os.path.getsize(arg)
                self.send_reply( 200, str(size))
            except:
                self.send_reply( 500, 'SIZE currently unsupported')
        else:
            self.send_reply( 257, 'SIZE on directory not possible')


    def doPasv( self, arg ):
        """
        passive mode
        """
        # (TODO) perhaps spawn new thread to handle the data stream                
        if self.datasock:
            self.datasock.close()
            
        # create a new stream socket for the data stream
        self.datasock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
     
        # find the next availiable port (todo test this)
        #p = self.server.getPort()
        self.dataport = -1
        for p in range(35535,40000):
            try:
                self.datasock.bind(('', p ))
                # listen for connection on data socket                
                self.datasock.listen(1)
                self.dataport = p
                break
            except:
                if self.server.debug:
                    print 'FTP : port ', p, 'in use skipping'
            
        if self.dataport == -1:
            if self.server.debug:
                print 'FTP : p > 40000, no port to use'
            self.send_reply( 500, 'port problem' )
            return

        # allow reuse of socket
        self.datasock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        #a = str(socket.gethostbyname(socket.gethostname())).split('.')
        a = self.server.getAddress().split('.')
        message = 'Passive mode ok (%d,%d,%d,%d,%d,%d)' % (int(a[0]),int(a[1]),int(a[2]),int(a[3]),(p >> 8) & 0xFF, p & 0xFF )
        self.send_reply( 227, message )
        self.passive = True

        
    def doRetr( self, arg ):
        """
        retrieve file
        """
        if arg == None:
            self.send_reply( 501, 'No filename specified')
            return

        if arg[0] != '/':     
            arg = os.path.normpath(self.cwd + '/' + arg)
        else:
            arg = os.path.normpath(self.home + '/' + arg)       
          
        # open file for read in txt mode
        try:
            if self.type == 1:
                fd = open( arg, mode='r')
            else:
                fd = open( arg, mode='rb')
        except IOError:
            self.send_reply( 550, 'failed to open ' +str(arg))
            return
        
        clientdata = self.create_datasock()
        if not clientdata:
            return
                    
        self.send_reply( 150, 'File status ok')               
        data = fd.read()
        clientdata.send(data)
        self.send_reply( 226, 'File sent')

        clientdata.close()
        fd.close()


    def doRest( self, arg ):
        """
        resume transfer
        """
        self.send_reply( 257, 'REST currently unsupported')

        
    def doMdtm( self, arg ):
        """
        returns the time the file was last modified
        """
        if arg[0] != '/':     
            arg = os.path.normpath(self.cwd + '/' + arg)
        else:
            arg = os.path.normpath(self.home + '/' + arg)
            
        if os.path.isfile( arg ):
            
            try:
                mtime = time.strftime('%Y%m%d%H%M%S', time.gmtime(os.path.getmtime( arg )))
                self.send_reply( 200, str(mtime))
            except:
                self.send_reply( 500, 'MDTM failed for file ' + str(arg))
                
        else:
            self.send_reply( 257, 'MDTM on direcotry unsupported')
        
    def doOpts( self, arg ):
        """
        IE sends this, not in RFC??
        """
        self.send_reply( 200, 'ok whatever ie')

        
    def run(self):
        """
        
        """
        self.send_reply( 220, "hello!!" )
        
        while not self.terminated:
            
            # wait for data to be recieved on socket and process it
            command = self.get_cmd()

            if not command:
                self.terminated = True
                continue
            
            cmd = str(command[0]).upper()
            arg = None
            
            if len(command) > 1:
                arg = command[1]

            if self.server.debug:       
                print 'FTP << ', cmd, arg
            
            if len(cmd) > 10:
                self.send_reply( 500, 'unknown command' )
                continue

            # process command            
            if cmd == 'USER'  :
                self.doUser( arg ) 
            elif cmd == 'PASS':
                self.doPassword ( arg )
            elif cmd == 'QUIT':
                self.doQuit()            
            elif cmd == 'NOOP':
                self.doNoop()
            elif cmd == 'SYST':
                self.doSyst()
            elif cmd == 'PORT' or cmd =='EPRT':
                self.doPort( arg )                
            elif cmd == 'PWD' or cmd == 'XPWD':           
                self.doPwd()
            elif cmd == 'CWD':
                self.doCwd( arg )
            elif cmd == 'CDUP':
                self.doCdup( arg )
            elif cmd == 'MKD' or cmd == 'XMKD':
                self.doMkd( arg )                    
            elif cmd == 'RMD' or cmd == 'XRMD':
                self.doRmd( arg )
            elif cmd == 'AUTH':
                self.doAuth( arg )
            elif cmd == 'TYPE':
                self.doType( arg )
            elif cmd == 'LIST' or cmd == 'NLST':
                self.doList( arg )
            elif cmd == 'SIZE':
                self.doSize( arg )
            elif cmd == 'MDTM':
                self.doMdtm( arg )
            elif cmd == 'REST':         
                self.doRest( arg )        
            elif cmd == 'RETR':
                self.doRetr( arg )            
            elif cmd == 'PASV':
                self.doPasv( arg )
            elif cmd == 'OPTS':
                self.doOpts( arg )
            elif cmd == 'RNFR':
                self.doRnfr( arg )
            elif cmd == 'RNTO':
                self.doRnto( arg )
            elif cmd == 'DELE':
                self.doDele( arg )
            else:       
                self.send_reply( 500, 'unknown command :' + str(cmd))

        # release sockets
        self.sock.close()
        if self.datasock:
            self.datasock.close()        

    def stop(self):
        """
        close client session
        """
        self.terminated = True


#-----------------------------------------------------------------------------------
# ftpServer
#
#-----------------------------------------------------------------------------------
class ftpServer(threading.Thread):
    """
    Keep track of server parameters, including used ports etc
    """
    def __init__(self, ip='10.20.4.2', port=21, homedir='.'):
        """
        
        """
        threading.Thread.__init__(self)
        self.highport = 35535
        self.port     = port
        self.ip       = ip
        self.homedir  = homedir
        self.terminated = False
        self.clientlist = []
        self.debug      = False
        
    def getAddress(self):
        """
        
        """
        # todo come up with a more intelligent method
        h, a, ip = socket.gethostbyname_ex(socket.gethostname())
        for i in ip:
            if i != '127.0.0.1':
                return i

        # this is not good.
        return self.ip
    
    def getPort(self):
        """
        
        """
        self.highport += 1
        # this is a bit of a hack, perhaps we should keep an used port list
        if self.highport > 40000:
            self.highport = 35535
            
        return self.highport

    def run(self):
        """
        
        """
        # creat an INET, STREAM socket
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # bind to port 21
        self.sock.bind(('', self.port))

        # listen for connections
        self.sock.listen(5)

        while not self.terminated:
            # use select
            r, w, x = [self.sock], [], []
            r, w, x = select.select(r, w, x, 1)
            if r:
                try:
                    # block until connection accepted        
                    (client, address) = self.sock.accept()
        
                    # fork new thread to handle this client
                    ct = ftpClient(client, self)
                    self.clientlist.append(ct)
                    ct.start()
                except:
                    if self.debug:
                        print 'FTP : client connect failed'

            # check what client threads still exist, remove from list if they are gone
            for i, ct in enumerate(self.clientlist):
                if not ct.isAlive():
                    ct.join()
                    self.clientlist.pop(i)

        # close socket
        self.sock.close()
        
        # check what client threads we have and kill them all wait till they all join
        for i, ct in enumerate(self.clientlist):
            if not ct.isAlive():
                ct.join()
            else:
                ct.stop()
                ct.join()       

    def stop(self):
        """
        close server down
        """
        self.terminated = True        


#-----------------------------------------------------------------------------------------------------
#  Helper functions (called by RATS framework)
#-----------------------------------------------------------------------------------------------------
FtpServer = ftpServer( ip='10.20.4.2', port=5000, homedir='/home/public/ftp/')
    
def startFtpServer():
    """
    """
    FtpServer.start()

def stopFtpServer():
    """
    """
    FtpServer.stop()
    FtpServer.join()

def getFtpServerAddress():
    """
    """
    return FtpServer.getAddress()

#-----------------------------------------------------------------------------------------------------
#  Test functions
#-----------------------------------------------------------------------------------------------------    
def test():
    print 'FTP server test'

    Ftp = ftpServer( ip='10.20.4.2', port=5000, homedir='.')
    Ftp.debug = True
    Ftp.start()
   
    while 1:
        pass
    
if __name__ == "__main__":
	test()
	

#
# $Log : $
#