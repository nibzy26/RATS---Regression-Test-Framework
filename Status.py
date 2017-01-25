import threading
from time import strftime

class status(object):
    """
    store a status message for each job
    """
    
    # dictionary stores the status for a single thread
    __status = {}
    __threads   = []
        
    def bind(self, jobId):        
        """
        bind the current thread to the jobId
        """
        #Get current number of bound threads
        numThreads = len(status.__threads)
        
        #Get name of currently executing thread and add to list
        threadName = threading.currentThread()#.getName()
        status.__threads.append((threadName, jobId))

        #Search for previously bound job id for the current thread
        for i in range(numThreads):
            name, jobId = status.__threads[i]
            if threadName is name:
                #Unbind previously bound job id for this thread
                status.__threads.pop(i)
                break
        
    def unbind(self):
        """
        break the bind between the current thread and its jobid
        """
        
        #Get name of currently executing thread
        threadName = threading.currentThread()#.getName()
        boundJobId = ""

        #Search for current thread in bound job id list
        for i, (name, jobId) in enumerate(status.__threads):
            if threadName is name:
                status.__threads.pop(i)
                boundJobId = jobId
                break

        #Search for jobId in other bound thread entries
        for (name, jobId) in enumerate(status.__threads):
            if jobId == boundJobId:
                return
        
        #No other threads bound to this job id, so remove it from dictionary
        status.__status.pop(boundJobId,'')


    def set(self, message, jobId=""):
        """
        set the status for the bound job id
        """
        if status.__status.has_key(jobId):
            status.__status[jobId] = message
            return
        
        threadName = threading.currentThread()#.getName()

        for (name, jobId) in status.__threads:
            if threadName is name:
                #print 'thread :', name, 'jobid :', jobId, 'message :', message
                status.__status[jobId] = message
                break
        
    def get(self, jobId):
        """
        get the status for a provided job id
        """
        return status.__status.get(jobId,'None')


def main():
    
    status2 = status()

    # map the current thread to the provided job id
    status2.bind('123456')

    # set the status to 'hello world'
    status2.set('hello world')

    # query status of the provided job, should be 'hello world'     
    print status2.get('123456')

    # create a new object to demonstrate sharing of status
    status3 = status()
    status3.set('goodbye world')

    # status should now be 'goodbye world'
    print status2.get('123456')

    # release the bind between thead and job id.
    status2.unbind()

    # demonstrate setting status on unmapped thread
    status3.set('hello again')

    # should still be 'goodbye world'    
    print status2.get('123456')
    
if __name__ == "__main__":
    main()    

    
