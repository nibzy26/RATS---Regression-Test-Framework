import socket, select

class NetworkError(Exception):
    """Base class for network error"""
    pass

class NoResponse(NetworkError):
    """No response arrived before timeout"""
    pass

class PtiInterface(object):
    def __init__(self, address="0.0.0.0"):
        self.address = address
        self.socket = None
        self.timeout = 10.0
        self.retries = 3

    def __del__(self):
        """Close socket when object is deleted"""
        try:
            self.close()
        except error.TransportError:
            pass

    def open(self):
        """Initialize PTI socket (port 26000) to be used for communication with terminal"""
        #print 'open', self.address
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, why:
            raise NetworkError('open() socket error: ' + str(why))
        try:
            self.socket.connect((self.address,26000))
        except socket.error, why:
            raise NetworkError('open() connect error: %s: %s' % (self.address, why))
        return self.socket

    def close(self):
        """Close PTI port"""
        if self.socket:
            try:
                self.socket.close()
            except socket.error, why:
                raise NetworkError('close() error: ' + str(why))
            self.socket = None

    def send(self, message):
        """Send message (string) to PTI port"""
        #print 'pti send:', self.address, ' :', message
        if not self.socket:
            self.open()
        try:
            self.socket.send(message)
        except socket.error, why:
            raise NetworkError('send() error: ' + str(why))

    def read(self):
        """Read data from the socket (assuming there's some data ready
           for reading), return a tuple of response message (as string)
           and source address 'src' (in socket module notation).
        """   
        if not self.socket:
            raise NetworkError('Socket not initialized')
        try:
            message = self.socket.recv(65536)
            if len(message) == 0:
                # disconnect from server
                raise NetworkError('recv() socket disconnected')
            
            #print 'pti response:', self.address, ':', message
        except socket.error, why:
            raise NetworkError('recv() error: ' + str(why))
        return message

    def receive(self):
        """
           Wait for incoming data from network, then read and return the
           available data as a tuple of received data item (as string) and
           source address, or timeout (and return a tuple of None's).
        """
        message = src = None
        if self.socket:
            r, w, x = [self.socket], [], []
            r, w, x = select.select(r, w, x, self.timeout)
            if r:
                message = self.read()
        return message

    def receive_non_block(self):
        """
           Check to see if there is for incoming data from network, then read and return the
           available data as a string
        """
        message = src = None
        if self.socket:
            r, w, x = [self.socket], [], []
            r, w, x = select.select(r, w, x, 0)
            if r:
                message = self.read()
                
        return message
    
    def send_and_receive(self, message):
        """
           Send and receive a message to/from the PTI port
           Return a tuple of data item (as string) and source address
           'src' (in socket module notation).
        """
        # retry once, the idea behind this is that if the remote end closes the connection
        # the read() function will fail with a NetworkError "connection reset by peer",
        # the retry is solely used to reestablish the connection with the remote unit.
        # if the retry fails then assume this wasn't the cause of the error and raise!
        retries = 1
        response = None
        message = "\r" + message
        while 1:
            try:
                #stuff = self.receive_non_block()
                #print 'PTI response', stuff
                
                self.send(message)
                #print 'PTI message', message
                response = self.receive()
                #print 'PTI response', response
                
                self.send("\r")
                response = self.receive()
                #print 'PTI response', response
                break
            except: # NetworkError:
                #self.close()
                #self.open()
                #if not retries:
                raise
                #retries -= 1
            
        if not response:
            raise NoResponse('No response arrived before timeout')
        return response