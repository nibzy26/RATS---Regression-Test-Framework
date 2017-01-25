from SimpleXMLRPCServer import SimpleXMLRPCServer
import xmlrpclib, select, socket
import threading
import time

class XMLRPCServer(threading.Thread, SimpleXMLRPCServer):

    allow_reuse_address = True
    
    def __init__(self, port):
        threading.Thread.__init__(self)
        SimpleXMLRPCServer.__init__(self, ('', port))
        
        self.register_introspection_functions()

    def run(self):

        self.terminated = False
        
        while not self.terminated:
            # Use select() to check if there is an incoming request
            r,w,e = select.select([self.socket], [], [], 1.0)
            if r:
                self.handle_request()
                
        self.socket.close()
        
    def terminate(self):
        self.terminated = True
        
#---------------TEST FUNCTIONS-----------------------------       
def adder_function(x,y):
    return x + y

class myobject:
    def __init__(self):
        self._id = 12
        
# Register an instance; all the methods of the instance are 
# published as XML-RPC methods (in this case, just 'div').
class MyFuncs:
    
    def __init__(self):
        self._id = 10
        self.list1 = []
        self.list1.append(1)
        self.list1.append('1')
        self.list1.append(2)
        self.list1.append('2')

    def setJobInfo(self, jobinfo):
        print jobinfo
        return 0
    
    def id(self):
        return self._id
    
    def div(self, x, y): 
        return x // y

    def getList(self):
        return self.list1

    def getObject(self):
        #me = myobject()
        return myobject() #xmlrpclib.dumps((me,),'PyObject')
    

def test_XMLRPCServer():
    print 'start server'
    
    server = XMLRPCServer(8000)
    server.register_function(pow)
    server.register_function(adder_function,'add')
    server.register_instance(MyFuncs())
    server.start()

    print 'server running'

    #
    # connect with server and call functions
    s = xmlrpclib.Server('http://localhost:8000')
    #socket.setdefaulttimeout(60)  
    print s.pow(2,3)  # Returns 2**3 = 8
    print s.add(2,3)  # Returns 5
    print s.div(5,2)  # Returns 5//2 = 2
    print s.id()
    print s.getList()
    p = s.getObject()
    print p['_id']
    print s.system.listMethods()

    # wait for server to join(), which in this case is never... opps
    #
    
    server.join()

    print 'done!'

if __name__ == "__main__":
    test_XMLRPCServer()    