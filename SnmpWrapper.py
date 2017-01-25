#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Snmp/SnmpWrapper.py,
"""Get/Set wrapper for PySNMP.

An SnmpWrapper is used to provide an abstract interface between higher-level components and the code
that actually performs SNMP transactions. This module contains one specific implementation based on
pysnmp-2.0.8 and SNMP protocol version 2c.

Unit tests are not provided for this module, however a simple test is performed if this module is executed.
"""

import time, types, errno, sys, select, string#, socket

class SnmpError(Exception):
    """
    Exception to be raised when a SNMP error occurs
    """

    def __init__(self, reason=""):
        """
        SnmpError exception constructor
        
        @type  reason: string
        @param reason: The reason for failure
        """
        self.reason = reason

    def __str__(self):
        return repr(self.reason)


class SnmpErrorNoSuchInstance(Exception):
    """
    Exception to be raised when a No Such Instance SNMP error occurs
    """

    def __init__(self, reason=""):
        """
        SnmpError exception constructor
        
        @type  reason: string
        @param reason: The reason for failure
        """
        self.reason = reason

    def __str__(self):
        return repr(self.reason)    
    

class SnmpWrapper(object):
    """Abstract base class for SNMP access.
    """
    def get(self, address, port, community, oid):
        """Perform an SNMP GET operation on a single object."""
        pass
    def set(self, address, port, community, oid, otype, value):
        """Perform an SNMP SET operation on a single object and value."""
        pass


from pysnmp import asn1, v2c
from pysnmp import role

class NonBlockRoleManager(role.manager):
    def receive(self):
        """
           receive() -> (message, src)
           
           Wait for incoming data from network or timeout (and return
           a tuple of None's).

           Return a tuple of received data item (as string) and source address
           'src' (in socket module notation).
        """
        # Make sure the connection exists
        if not self.socket:
            raise NetworkError('Socket not initialized')

        # Initialize sockets map
        r, w, x = [self.socket], [], []

        # Wait for response
        start = time.time()
        while (time.time() - start) < self.timeout:
            rr, rw, rx = select.select(r, w, x, 0.2)
            if rr:
                return self.read()
            time.sleep(1)

        # Return nothing on timeout
        return(None, None)
    

class SnmpWrapperPySnmp(SnmpWrapper):
    """Specialised SNMP wrapper for PySNMP module (originally written for pysnmp-2.0.8, SNMP version 2c)."""
    def __init__(self):
        pass

    def get(self, address, port, community, soid, retry=True):
        #print "SNMP get of : ", address, port, community, soid
        if retry:
            netRetries = 5
            sockRetries = 5
            cmdRetries = 15
        else:
            netRetries = 1
            sockRetries = 1
            cmdRetries = 1
        timeout    = 10.0
        #socket.setdefaulttimeout(1.0)
        
        while cmdRetries:
         
            # Create SNMP manager object
            client = role.manager((address, port))
            client = NonBlockRoleManager((address, port))

            # Pass it a few options
            client.timeout = timeout
            client.retries = netRetries

            # Create SNMP request & response objects
            req = v2c.GETREQUEST()
            rsp = v2c.GETRESPONSE()

            # Encode OIDs, encode SNMP request message and try to send
            # it to SNMP agent and receive a response
            oid = asn1.OBJECTID().encode(soid)
            msg = req.encode(community=community, encoded_oids=[oid])
            #print 'SNMP get request : ', req
            try:
                (answer, src) = client.send_and_receive(msg)
            except role.NetworkError, why:
                sockRetries -= 1
                if not sockRetries:
                    raise SnmpError, str(sys.exc_info()[1])

                # (TODO) handle errors on close                
                client.close()

                # retry                
                del client
                time.sleep(5)
                continue
            
            # (TODO) handle error on close
            client.close()
            del client
            
            # Decode SNMP response
            rsp.decode(answer)
            #print 'SNMP get response : ', rsp
            
            # Make sure response matches request (request IDs, communities, etc)
            if req != rsp:
                raise SnmpError, 'Unmatched response: %s vs %s' % (str(req), str(rsp))

            # Check for remote SNMP agent failure
            if rsp['error_status']:
                raise SnmpError, 'SNMP error #' + str(rsp['error_status']) + ' for OID #' + str(soid)
            else:
                # decode and check for noSuchInstance, noSuchObject
                # this is only required for SNMPv2
                snmpV2Error = 0
                decoded_vals = map(asn1.decode, rsp['encoded_vals'])
                for val in decoded_vals:
                    
                    if string.find(str(val[0]), "noSuchInstance") != -1 or \
                       string.find(str(val[0]), "noSuchObject") != -1 or \
                       string.find(str(val[0]), "endOfMibView") != -1:
                        snmpV2Error = 1
                        break

                if snmpV2Error:
                    cmdRetries -= 1
                    if not cmdRetries:
                        raise SnmpErrorNoSuchInstance, "SNMP Error : noSuchInstance for OID " + str(soid)

                    #print "SNMP Retry because noSuchInstance for OID ", soid, address
                    time.sleep(5)
                    continue

                # Decode BER encoded values associated with Object IDs.
                vals = map(lambda x: x[0](), decoded_vals)
                break
           
            time.sleep(1)
            
        # Print out results
        #print "get:"
        #for (oid, val) in map(None, oids, vals):
        #    print oid + ' ---> ' + str(val)
        return vals[0]


    def set(self, address, port, community, soid, otype, value, retry=True):
        #print "SNMP set of : ", address, port, community, soid, value
        if retry:
            netRetries = 5
            sockRetries = 5
            cmdRetries = 15
        else:
            netRetries = 1
            sockRetries = 1
            cmdRetries = 1
        timeout = 10.0
        #version = '2c'
        oid = "."+soid        
        while cmdRetries:
            # Create SNMP manager object
            client = role.manager((address, port))
            #client.socket = None
            
            # Pass it a few options
            client.timeout = timeout
            client.retries = netRetries

            # Create SNMP request & response objects
            req = v2c.SETREQUEST()
            rsp = v2c.GETRESPONSE()

            encoded_oids = []
            encoded_vals = []

            #    for (oid, otype, val) in varargs:
            #        encoded_oids.append(asn1.OBJECTID().encode(oid))
            #        encoded_vals.append(eval('asn1.'+otype+'()').encode(val))

            encoded_oids.append(asn1.OBJECTID().encode(oid))
            encoded_vals.append(eval('asn1.' + otype + '()').encode(value))

            # Encode OIDs along with their respective values, encode SNMP
            # request message and try to send it to SNMP agent and receive
            # a response
            msg = req.encode(community=community, encoded_oids=encoded_oids, encoded_vals=encoded_vals)
            #print 'SNMP set request : ', req
            try:
                (answer, src) = client.send_and_receive(msg)
            except role.NetworkError, why:
                sockRetries -= 1
                if not sockRetries:
                    raise SnmpError, str(sys.exc_info()[1])

                # (TODO) handle errors on close                
                client.close()

                # retry                
                del client
                time.sleep(5)
                continue

            # (TODO) handle error on close
            client.close()
            del client
            
            # Decode SNMP response message
            rsp.decode(answer)
            #print 'SNMP set response : ', rsp
            # Make sure response matches request (request IDs, communities, etc)
            if req != rsp:
                raise SnmpError, 'Unmatched response: %s vs %s' % (str(req), str(rsp))

            # Check for remote SNMP agent failure
            if rsp['error_status']:

                # common errors (from MS site ;)
                """
                0 	SNMP_ERRORSTATUS_NOERROR - The agent reports that no errors occurred during transmission.
                1 	SNMP_ERRORSTATUS_TOOBIG  - The agent could not place the results of the requested SNMP operation in a single SNMP message.
                2 	SNMP_ERRORSTATUS_NOSUCHNAME - The requested SNMP operation identified an unknown variable.
                3 	SNMP_ERRORSTATUS_BADVALUE - The requested SNMP operation tried to change a variable but it specified either a syntax or value error.
                4 	SNMP_ERRORSTATUS_READONLY - The requested SNMP operation tried to change a variable that was not allowed to change, according to the community profile of the variable.
                5 	SNMP_ERRORSTATUS_GENERR - An error other than one of those listed here occurred during the requested SNMP operation.
                6 	SNMP_ERRORSTATUS_NOACCESS - The specified SNMP variable is not accessible.
                7 	SNMP_ERRORSTATUS_WRONGTYPE - The value specifies a type that is inconsistent with the type required for the variable.
                8 	SNMP_ERRORSTATUS_WRONGLENGTH - The value specifies a length that is inconsistent with the length required for the variable.
                9 	SNMP_ERRORSTATUS_WRONGENCODING - The value contains an Abstract Syntax Notation One (ASN.1) encoding that is inconsistent with the ASN.1 tag of the field.
                10 	SNMP_ERRORSTATUS_WRONGVALUE - The value cannot be assigned to the variable.
                11 	SNMP_ERRORSTATUS_NOCREATION - The variable does not exist, and the agent cannot create it.
                12 	SNMP_ERRORSTATUS_INCONSISTENTVALUE - The value is inconsistent with values of other managed objects.
                13 	SNMP_ERRORSTATUS_RESOURCEUNAVAILABLE - Assigning the value to the variable requires allocation of resources that are currently unavailable.
                14 	SNMP_ERRORSTATUS_COMMITFAILED - No validation errors occurred, but no variables were updated.
                15 	SNMP_ERRORSTATUS_UNDOFAILED - No validation errors occurred. Some variables were updated because it was not possible to undo their assignment.
                16 	SNMP_ERRORSTATUS_AUTHORIZATIONERROR - An authorization error occurred.
                17 	SNMP_ERRORSTATUS_NOTWRITABLE - The variable exists but the agent cannot modify it.
                18 	SNMP_ERRORSTATUS_INCONSISTENTNAME - The variable does not exist; the agent cannot create it because the named object instance is inconsistent with the values of other managed objects.
                """
                if int(rsp['error_status']) != 14 and \
                   int(rsp['error_status']) != 15:
                    raise SnmpError, 'SNMP error #' + str(rsp['error_status']) + ' for OID #' + str(oid)


                # see if value on radio already matches what we are trying to set it to.
                #res = self.get(address, port, community, soid)
                #if res[0] == value:
                #    print 'values match, assumed set ok'
                #    return res
                    
                cmdRetries -= 1
                if not cmdRetries:
                    raise SnmpError, 'SNMP error #' + str(rsp['error_status']) + ' for OID #' + str(oid)
                #if int(rsp['error_status']) != 14:
                #    print "SNMP Retry because error ", str(rsp['error_status']),"for OID ", oid
                time.sleep(5)
                continue                       
            else:
                # decode and check for noSuchInstance, noSuchObject
                # this is only required for SNMPv2
                snmpV2Error = 0
                decoded_vals = map(asn1.decode, rsp['encoded_vals'])
                for val in decoded_vals:
                    
                    if string.find(str(val[0]), "noSuchInstance") != -1 or \
                       string.find(str(val[0]), "noSuchObject") != -1 or \
                       string.find(str(val[0]), "endOfMibView") != -1:
                        snmpV2Error = 1
                        break

                if snmpV2Error:
                    raise SnmpErrorNoSuchInstance, "SNMP Error : noSuchInstance for OID " + str(soid)

                # Decode BER encoded values associated with Object IDs.
                vals = map(lambda x: x[0](), decoded_vals)
                break

            time.sleep(1)

        #print "set:"
        #for (oid, val) in map(None, oids, vals):
        #    print oid + ' ---> ' + str(val)

        # return the first value
        return vals[0]

def test():
    s = SnmpWrapper()

    val = s.get('10.16.9.183', 161, 'terminal', '.1.3.6.1.4.1.2509.8.14.2.1.1.3' + '.6')
    s.set('10.16.9.183', 161, 'terminal', '.1.3.6.1.4.1.2509.8.14.2.1.1.3' + '.6', 'OCTETSTRING', 'hello')
    print s.get('10.16.9.183', 161, 'terminal', '.1.3.6.1.4.1.2509.8.14.2.1.1.3' + '.6')
    s.set('10.16.9.183', 161, 'terminal', '.1.3.6.1.4.1.2509.8.14.2.1.1.3' + '.6', 'OCTETSTRING', val)
    print s.get('10.16.9.183', 161, 'terminal', '.1.3.6.1.4.1.2509.8.14.2.1.1.3' + '.6')

if __name__ == "__main__":
    test()

#
#
