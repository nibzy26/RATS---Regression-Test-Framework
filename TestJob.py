import JobRunner
from Enum.eTestStatus import eTestStatus

class JobStatus(object):
    """
    """
    def __init__(self):
        """
        """
        self.currentTest = ""
        self.numTests    = 0
        self.totalTime   = 0.0
        self.testStatus  = {}

    def numTests(self):
        return len(self.testStatus)

    def numDone(self):
        return len([1 for test in self.testList if test.status.state = "Pending"])
        return len([1 for test in self.testList if test.status.state = "Running"])
        return len([1 for test in self.testList if test.status.state = "Pass"])
        return len([1 for test in self.testList if test.status.state = "Fail"])

    def numDone(self):
        return len(self.testStatus)

    def numDone(self):
        return len(self.testStatus)

class TestStatus(object):
    """
    """
    def __init__(self):
        """
        """
        self.testTime  = 0.0
        self.state     = eTestStatus.UNKNOWN

[net, link, terminal, test, iters, Status]

"""
Take list of tests/networks/links/terminals/iters
create separate list for each network
[unique id, link, terminal, test, iters]
each list is a job
output lists to front end

"""


class TestSpec(object):
    def __init__(self):
        self.entryId    = 0 #Unique id for entry in task list
        self.linkId     = 0
        self.terminalId = 0
        self.testId     = 0
        self.testIters  = 0
        self.status     = TestStatus()

class TestJob(object):
    """
    """

    def __init__(self):
        """
        """
        #Tests to run
        self.testList = {} #dictionary of TestSpec() objects

        self.networkId  = 0
        #self.linkId     = 0 from test spec
        #self.terminalId = 0 from test spec
        
        #Test Status
        self.status = 

    def prepare(self):
        self.status.testTime = 0.0
        test.status.result = "Pending"
        for test in self.testList.values:
            test.status.testTime = 0.0
            test.status.result = "Pending"
