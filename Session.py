#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Snmp/Session.py,

"""
Session module.
Defines Session and ContextSession classes and associated exceptions.
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import time

class SessionError(Exception):
    """Base class for exceptions in this module."""
    pass

class InvalidTranslatorError(SessionError):
    """Exception raised for invalid translator instance."""
    pass

class InvalidSnmpWrapperError(SessionError):
    """Exception raised for invalid snmp wrapper instance."""
    pass


class Session(object):
    """
    A Session object maintains context for SNMP GET/SET operations.

    When initialised, the Session is given a Translator object which is used to perform the conversion
    between symbolic Object Names and SNMP Object IDs (OIDs). To best utilise the Translator cache, a
    single instance may be passed to multiple Sessions. An SnmpWrapper object is also required to
    perform the actual SNMP transactions.
    """
    def __init__(self, address='', community='terminal', port=161, translator=None, snmp_wrapper=None):
        """
        Session class constructor.

        @type    translator: Translator
        @param   translator: The translator which will provide the necessary object IDs
        @type  snmp_wrapper: SnmpWrapper
        @param snmp_wrapper: The wrapper to be used for SNMP communication
        @type       address: string
        @param      address: The IP address of the terminal to communicate with
        @type          port: int
        @param         port: The port to use for SNMP communications
        @type     community: string
        @param    community: The SNMP community string to use
        """
        if not translator:
            raise InvalidTranslatorError, "A valid Translator instance is required"
        if not snmp_wrapper:
            raise InvalidSnmpWrapperError, "A valid SNMP Wrapper instance is required"
        self.translator = translator
        self.snmp_wrapper = snmp_wrapper
        self.address = address
        self.port = port
        self.community = community

    def get(self, object_name, instance):
        """
        Perform SNMP get for the specified object and instance.

        @type  object_name: string
        @param object_name: The name of the object to get the value of
        @type     instance: int or string
        @param    instance: The instance of the object to get the value for
        @rtype:  Data type of the requested object
        @return: The value of the specified object and instance
        """
        (oid, otype) = self.translator.translate(object_name)
        oid = oid + '.' + str(instance)
        return self.snmp_wrapper.get(self.address, self.port, self.community, oid)

    def set(self, object_name, instance, value):
        """
        Perform SNMP set for the specified object, instance and value.

        @type  object_name: string
        @param object_name: The name of the object to set the value of
        @type     instance: int or string
        @param    instance: The instance of the object to set the value for
        @type        value: Data type of the specified object
        @param       value: The value to set
        @rtype:  Data type of the specified object
        @return: The value of the specified object and instance
        """
        (oid, otype) = self.translator.translate(object_name)
        oid = oid + '.' + str(instance)
        return self.snmp_wrapper.set(self.address, self.port, self.community, oid, otype, value)


class ContextSession(object):
    """
    A Session object maintains context for SNMP GET/SET operations.

    When initialised, the Session is given a Translator object which is used to perform the conversion
    between symbolic Object Names and SNMP Object IDs (OIDs). An SnmpWrapper object is also provided to
    perform the actual SNMP transactions.
    For efficiency, the Translator and SnmpWrapper are common to all instances

    Language Extension:
    A ContextSession has methods which extend the Python language to provide specific contexts for a session.
    By default, the .set and .get methods use the community string specified when the instance is created.
    These methods may also be used with a prefixed context to automatically select the required community string.
    The contexts 'terminal', 'odu', 'slot' and 'prot' are available, referring to the active context in each case.
    Inactive contexts may also be referred to as 'terminal_i', 'odu_i', 'slot_i' and 'prot_i'. In addition, the
    odu, slot and prot contexts are indexed. i.e. slot_i[3].get will use the communiity string 'slot3_i'
    """
    _supportedContexts = ["terminal", "odu", "slot", "prot"]
    _translator=None
    _snmp_wrapper=None
    _pti_wrapper=None
    _oag_wrapper=None

    def __init__(self, address='', community='terminal', port=161, translator=None, snmp_wrapper=None, pti_wrapper=None, oag_wrapper=None):
        """
        ContextSession object constructor

        @type       address: string
        @param      address: The IP address of the terminal to communicate with
        @type     community: string
        @param    community: The SNMP community string to use
        @type    translator: Translator
        @param   translator: The translator which will provide the necessary object IDs
        @type  snmp_wrapper: SnmpWrapper
        @param snmp_wrapper: The wrapper to be used for SNMP communication
        @type   pti_wrapper: PtiWrapper
        @param  pti_wrapper: The wrapper to be used for PTI communication
        @type          port: int
        @param         port: The port to use for SNMP communications
        """
        self.address = address
        self.port = port
        self.community = community
        self._context = ""
        self.numRetries = 5
        if translator:
            ContextSession._translator = translator
        elif not ContextSession._translator:
            raise InvalidTranslatorError, "A valid Translator instance is required"
        if snmp_wrapper:
            ContextSession._snmp_wrapper = snmp_wrapper
        elif not ContextSession._snmp_wrapper:
            raise InvalidSnmpWrapperError, "A valid SNMP Wrapper instance is required"
        if pti_wrapper:
            self._pti_wrapper = pti_wrapper()
        elif not ContextSession._pti_wrapper:
            raise InvalidSnmpWrapperError, "A valid PTI Wrapper instance is required"
        if oag_wrapper and not self._oag_wrapper:
            self._oag_wrapper = oag_wrapper(self.address)
        elif not ContextSession._oag_wrapper:
            raise InvalidSnmpWrapperError, "A valid OAG Wrapper instance is required"

    def __getattr__(self, name):
        """
        Called when a class attribute could not be found.
        If the attribute is a valid context name, then it is stored to be
        used with the get and set methods, otherwise an exception is raised.
        
        @type  name: string
        @param name: The name of the attribute that could not be found
                     May contain a context name specified as part of a get or set method call
        @rtype:  ContextSession
        @return: self
        """
        findName = name
        if name.endswith("_i"):
            findName = name[:-2]
        else:
            findName = name
        if findName in ContextSession._supportedContexts:
            self._context = name
            return self
        raise AttributeError, "Attribute does not exist"

    def __getitem__(self, key):
        """
        Called when a non existent class attribute is indexed.
        If the index is part of a valid context reference, then it is stored to
        be used with the get and set methods, otherwise an exception is raised.

        @type  key: integer
        @param key: The index of the attribute that could not be found
                    May contain an indexed context specified as part of a get or set method call
        @rtype:  ContextSession
        @return: self
        """
        if not self._context:
            raise TypeError, "Object cannot be indexed"
        if self._context.endswith("_i"):
            self._context = self._context[:-2] + str(key) + "_i"
        else:
            self._context += str(key)
        return self

    def get(self, object_name, instance, retry=True):
        """
        Perform SNMP get for the specified object and instance.

        @type  object_name: string
        @param object_name: The name of the object to get the value of
        @type     instance: int or string
        @param    instance: The instance of the object to get the value for
        @rtype:  Data type of the requested object
        @return: The value of the specified object and instance
        """
        if self._context:
            community = self._context
        else:
            community = self.community
            
        (oid, otype) = ContextSession._translator.translate(object_name)
        if oid:
            oid = oid + '.' + str(instance)
            #print "SNMP Get:",self.address, community, object_name, oid
            result = ContextSession._snmp_wrapper.get(self.address, self.port, community, oid, retry)
        else:
            #Mib object not found - try Pti interface
            result = self.pti_get(object_name, instance, retry)

        self._context = ""
        return result

    def oag_get(self, object_name, instance):
        """
        Perform OAG get for the specified object and instance.

        @type  object_name: string
        @param object_name: The name of the object to get the value of
        @type     instance: int or string
        @param    instance: The instance of the object to get the value for
        @rtype:  Data type of the requested object
        @return: The value of the specified object and instance
        """
        if self._context:
            community = self._context
        else:
            community = self.community
       
        result = self._oag_wrapper.get(community, object_name, str(instance))
        try:
            if str(int(result)) == result:
                result = int(result)
        except:
            pass
        self._context = ""
        return result
    
    def pti_get(self, object_name, instance, retry=True):
        """
        Perform PTI get for the specified object and instance.

        @type  object_name: string
        @param object_name: The name of the object to get the value of
        @type     instance: int or string
        @param    instance: The instance of the object to get the value for
        @rtype:  Data type of the requested object
        @return: The value of the specified object and instance
        """
        if self._context:
            community = self._context
        else:
            community = self.community

        #print 'IP = ', self.address
        
        result = self._pti_wrapper.get(self.address, community, object_name, str(instance), retry)
        try:
            if str(int(result)) == result:
                result = int(result)
        except:
            pass
        self._context = ""
        return result

    def set(self, object_name, instance, value, retry=True):
        """
        Perform SNMP set for the specified object, instance and value.

        @type  object_name: string
        @param object_name: The name of the object to set the value of
        @type     instance: int or string
        @param    instance: The instance of the object to set the value for
        @type        value: Data type of the specified object
        @param       value: The value to set
        @rtype:  Data type of the specified object
        @return: The value of the specified object and instance
        """
        if self._context:
            community = self._context
        else:
            community = self.community
        (oid, otype) = ContextSession._translator.translate(object_name)
        try:
            if str(int(value)) == value:
                value = int(value)
        except:
            pass
        
        if oid:
            oid = oid + '.' + str(instance)
            #print "SNMP Set:",self.address, community, object_name, oid, value
            result = ContextSession._snmp_wrapper.set(self.address, self.port, community, oid, otype, value, retry)
        else:
            #Mib object not found - try Pti interface
            result = self.pti_set(object_name, instance, value, retry)
        self._context = ""
        return result

    def pti_set(self, object_name, instance, value, retry=True):
        """
        Perform PTI set for the specified object, instance and value.

        @type  object_name: string
        @param object_name: The name of the object to set the value of
        @type     instance: int or string
        @param    instance: The instance of the object to set the value for
        @type        value: Data type of the specified object
        @param       value: The value to set
        @rtype:  Data type of the specified object
        @return: The value of the specified object and instance
        """
        if self._context:
            community = self._context
        else:
            community = self.community
            
        #print 'IP = ', self.address
        result = self._pti_wrapper.set(self.address, community, object_name, str(instance), str(value), retry)
        try:
            if str(int(result)) == result:
                result = int(result)
        except:
            pass
        self._context = ""
        return result

    def oag_set(self, object_name, instance, value):
        """
        Perform OAG set for the specified object, instance and value.

        @type  object_name: string
        @param object_name: The name of the object to set the value of
        @type     instance: int or string
        @param    instance: The instance of the object to set the value for
        @type        value: Data type of the specified object
        @param       value: The value to set
        @rtype:  Data type of the specified object
        @return: The value of the specified object and instance
        """
        if self._context:
            community = self._context
        else:
            community = self.community
            
        result = self._oag_wrapper.set(community, object_name, str(instance), str(value))
        try:
            if str(int(result)) == result:
                result = int(result)
        except:
            pass
        self._context = ""
        return result    

    def pti_close(self):
        """
        Close PTI session
        """
        self._pti_wrapper.close()


    def resetConfig(self):
        
        #print 'deleting inactive'
        try:
            self.terminal_i.set( 'configCommitResetBuffer', 0, 1 )
        except:
            #print 'resetConfig error'
            return False
        
        retries = 10
        while retries:
            retries =- 1
            try:
                status = self.terminal_i.get('configCommitResetBuffer', 0 )

                if status == 0:
                   #print 'idle'
                    pass
                elif status == 2:
                   #print 'reseting'
                    pass
                elif status == 3:
                   #print 'success'
                   break
                elif status == 4:
                   #print 'failed'
                   return False
                else:
                   print '???', status
            
            except:
                pass
            time.sleep(5)

        return True            
                
                
    def activateConfig(self):
        """Sends SNMP set requests required to switch a terminal's configuraton

            returns : True if commit ok, False if commit failed
        """
        try:
            self.terminal_i.set("configCommitRevertduration", 0, 0)
            self.terminal_i.set("configCommitSave", 0, 1)
        except:
            #print 'activateConfig error'
            return False

        # allow up to 60 seconds for save?        
        retries = 30
        while retries:
            retries -= 1
            try:
                status = self.terminal_i.get("configCommitSave", 0)
                #  idle(0), save(1), saving(2), success(3), failed(4)
                if status == 0:
                    #print 'idle!'
                    break
                elif status == 2:
                    #print 'saving'
                    pass
                elif status == 3:
                    #print 'success, saved'
                    break
                elif status == 4:
                    #print 'save failed'
                    return False
            except:
                pass
            time.sleep(5)

        # do config switch
        try:            
            self.terminal_i.set("configCommitSwitch", 0, 1)
        except:
            print 'activateConfig error'
            return False
        
        retries = 30# self.numRetries
        while retries:
            retries -= 1
            try:
                #status = self.terminal.get("configStatus", 0)
                status = self.terminal_i.get("configCommitSwitch", 0)
                #  idle(0), switch(1), switching(2), success(3), failed(4)
                
                if status == 0:
                    #print 'idle'
                    break
                elif status == 2:
                    #print 'switching'
                    pass
                elif status == 3:
                    #print 'success'
                    break
                elif status == 4:
                    #print 'failed'
                    return False
            except:
                pass
            time.sleep(5)

        return True            

class PtiSession(object):
    """
    A Session object for PTI GET/SET operations.
    """
    _pti_wrapper=None

    def __init__(self, address='', pti_wrapper=None):
        """
        PtiSession object constructor
        """
        self.address = address
        self.port = port
        self.numRetries = 5
        if pti_wrapper:
            self._pti_wrapper = _pti_wrapper()
        elif not self._pti_wrapper:
            raise InvalidSnmpWrapperError, "A valid SNMP Wrapper instance is required"

    def setcontext(self, context_name):
        """
        Perform get for the specified object and instance.
        """
        text = "context " + str(context_name) + "\r"
        result = self._pti_wrapper.set(self.address, text)
        return result

    def get(self, object_name, instance):
        """
        Perform get for the specified object and instance.
        """
        text = object_name + " " + str(instance) + "\r"
        result = self._pti_wrapper.get(self.address, text)
        return result

    def set(self, object_name, instance, value):
        """
        Perform set for the specified object, instance and value.
        """
        text = object_name + " " + str(instance) + " " + str(value) + "\r"
        result = self._pti_wrapper.set(self.address, text)
        return result

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#
