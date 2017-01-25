#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Snmp/PyTranslator.py,

"""
Implements a translator from MIB object names to OIDs
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import cPickle, os, re
import Translator

class _TokenFile(file):
    """
    Class for reading an input text file as a series of tokens
    """

    def __init__(self, *args, **kwargs):
        """
        Token file object constructor.
        Initialises the instance, and opens the specified file for reading

        @type    *args: list
        @param   *args: Accepts arguments that would normally be passes to the file.open() method
        @type  *kwargs: list
        @param *kwargs: Accepts keyword arguments that would normally be passed to the file.open() method
        """
        file.__init__(self, *args, **kwargs)
        self.token          = "" #Token read from file
        self.previousToken  = "" #Previous token read from file
        self.__textline     = "" #Line of text read from file, & being processed.
        self.lineno = 0

    def getToken(self, delimiters):
        """
        Gets a token from the file, separated by one of the specified delimiters

        @type  delimiters: string
        @param delimiters: Delimiters to use for separating tokens
        @rtype:  string
        @return: Next token from file separated by specified delimiters
        """
        #If token is valid, save as previous token
        if self.token:
            self.previousToken = self.token
            self.token = ""
        #If text read from file is empty, read another line
        if not self.__textline:
            self.__textline = self.readline()
            self.lineno += 1
        #Loop until token is found, or end of file is reached
        while self.__textline and not self.token:
            #Tokenise the text read from the file using the specified delimiters
            splittext = re.split("[" + delimiters + "]", self.__textline, 1)
            #Token was found, save rest of text for next search
            if len(splittext) > 1:
                self.token = splittext[0]
                self.__textline = splittext[1]
                if not self.__textline:
                    self.__textline = self.readline()
                    self.lineno += 1
            else:
                #Token not found yet, read another line
                self.__textline = self.readline()
                self.lineno += 1
        return self.token
    
    def findToken(self, tokentofind, delimiters):
        """
        Find a specified token in the file, ignoring occurrences that
        are in quotes, and return the token following the one specified.

        @type  tokentofind: string
        @param tokentofind: Specific token to search for
        @type   delimiters: string
        @param  delimiters: Delimiters to use for finding the next token after the specified one
        @rtype:  string
        @return: Next token from file separated by specified delimiters
                 which follows the occurrence of the specified token
        """
        quotecount = 0 #Used to count number of quotation marks
        #Loop until we run out of tokens
        while self.getToken(" \t\n\r"):
            #Get number of quotation marks in token
            quotecount += self.token.count("\"")
            #Continue loop if number of quotation marks is odd
            if quotecount % 2 != 0:
                continue
            #Exit loop if token match is found
            if self.token == tokentofind:
                break
        return self.getToken(delimiters)


class _MibObject(object):
    """Stores information for a MIB object"""
    def __init__(self):
        """MIB Object information class constructor"""
        self.name = ""
        """Name of MIB object"""
        self.syntax = ""
        """MIB object data type"""
        self.oid = ""
        """OID of MIB object"""
        self.branch = ""
        """Branch number of MIB object"""
        self.parentName = ""
        """Name of MIB object's parent"""
        self.parent = None
        """Instance of MIB object's parent"""


class PyTranslator(Translator.Translator):
    """
    Interprets MIB definition files and provides method to
    translate from an Object Name to the associated OID.
    """
    def __init__(self, directory="./Snmp/mibs/"):
        """
        Mib Translator Constructor.
        
        @type  directory: string
        @param directory: The directory containing the MIB files
        """
        self._mibDir = directory
        self._objectList = []
        self._objectDict = {}
        self._tcDict = {}
        self._objectTypes = {}
        if not self._loadOidDictionary():
            self.mibRefresh()

    def translate(self, objectName):
        """
        Returns a tuple containing the (OID, DataType) for the specified object name

        @type  objectName: string
        @param objectName: The name of the MIB object whose OID should be returned
        @rtype:  tuple
        @return: (OID, DataType) strings for specified MIB object if found, empty strings otherwise
        """
        if objectName and self._objectDict.has_key(objectName.lower()):
            return self._objectDict[objectName.lower()]
        else:
            return (None, None)

    def mibRefresh(self, directory=""):
        """
        Refreshes MIB information - Recreates OID dictionary from scratch

        @type  directory: string
        @param directory: The directory containing the MIB files.
                          Only required if different from previously specified
        """
        if directory: self._mibDir = directory
        self._objectTypes = {
            "BOOLEAN":       "INTEGER",
            "TruthValue":    "INTEGER",
            "INTEGER":       "INTEGER",
            "Integer32":     "INTEGER",
            "DisplayString": "OCTETSTRING",
            "IpAddress":     "IPADDRESS",
            "NetworkAddress":"IPADDRESS",
            "Counter32":     "COUNTER32",
            "Counter":       "COUNTER32",
            "Gauge32":       "GAUGE32",
            "Gauge":         "GAUGE32",
            "TimeTicks":     "TIMETICKS",
            "Unsigned":      "UNSIGNED32",
            "Unsigned32":    "UNSIGNED32",
            "OCTET":         "OCTETSTRING",
            "OBJECT":        "OBJECTID",
            "DateAndTime":   "OCTETSTRING",
            "none":          "" }
        self._createMergedMib()
        self._parseMergedMib()
        self._buildOidDictionary()
        self._saveOidDictionary()
        #Free memory used by objects that are no longer needed
        del self._objectList
        del self._tcDict
        del self._objectTypes

    def _loadOidDictionary(self):
        """
        Loads previously saved OID dictionary from file
        @rtype:  boolean
        @return: True if dictionary was loaded successfully, False otherwise
        """
        result = True
        oidFile = None
        try:
            filename = self._mibDir + "oids.dat"
            oidFile = open(filename, 'rb')
            self._objectDict = cPickle.load(oidFile)
        except:
            result = False
        if oidFile:
            oidFile.close()
        return result

    def _saveOidDictionary(self):
        """
        Saves OID dictionary to a file

        @rtype:  boolean
        @return: True if dictionary was saved successfully, False otherwise
        """
        result = True
        oidFile = None
        try:
            filename = self._mibDir + "oids.dat"
            oidFile = open(filename, 'wb')
            cPickle.dump(self._objectDict, oidFile, cPickle.HIGHEST_PROTOCOL)
        except:
            result = False
        if oidFile:
            oidFile.close()
        return result

    def _createMergedMib(self):
        """
        Created a single merged file from all the MIBS in the assigned directory
        Overwrites any existing merged MIB.
        """
        #Extensions MUST be processed in the following particular
        #order to ensure that Objects are assigned the correct OID.
        mibFiles = []
        for extension in (".MI2",".MIB",".mi2",".mib",".txt"):
            for filename in os.listdir(self._mibDir):
                if filename.endswith(extension):
                    mibFiles.append(self._mibDir + filename)
       
        if mibFiles:
            mergedMib = open(self._mibDir + "merged_mib.dat", "w")
            for filename in mibFiles:
               mibFile = open(filename, 'r')
               mibData = mibFile.read()
               mibFile.close()
               mergedMib.write(filename)
               mergedMib.write(mibData)
            mergedMib.close()

    def _parseMergedMib(self):
        """
        Parses the merged file containing all the MIB information
        Creates a list of MIB object information
        """
        self._objectList = []
        mibFile = _TokenFile(self._mibDir + "merged_mib.dat")
        objectInfo = _MibObject()
        while mibFile.getToken(" \t\n\r\{}:=\(\)"):
            if mibFile.token == "OBJECT":
                objectInfo.name = mibFile.previousToken
                if mibFile.getToken(" \t\n\r") == "IDENTIFIER":
                    objectInfo.parentName = mibFile.findToken("::=", " \t\n\r\{\(")
                    objectInfo.branch = mibFile.getToken(" \t\n\r}")
                    self._objectList.append(objectInfo)
                    objectInfo = _MibObject()

            elif mibFile.token == "OBJECT-TYPE":
                objectInfo.name = mibFile.previousToken
                if mibFile.getToken(" \t\n\r") == "SYNTAX":
                    objectInfo.syntax = mibFile.getToken(" \t\n\r\(\{")
                    if mibFile.token == "INTEGER":
                        if mibFile.getToken(" \t\n\r\(:") == "{":
                            while mibFile.token != "}":
                                if mibFile.getToken(" \t\n\r\(:") == "--":
                                    mibFile.getToken("\t\n\r")
                                else:
                                    mibFile.getToken(" \t\n\r\(\):")
                                    if mibFile.getToken(" \t\n\r\):") != ",": break
                elif mibFile.token != "STATUS": continue
                objectInfo.parentName = mibFile.findToken("::=", " \t\n\r\{\(")
                objectInfo.branch = mibFile.getToken(" \t\n\r}\)")
                self._objectList.append(objectInfo)
                objectInfo = _MibObject()
                
            elif mibFile.token == "MODULE-IDENTITY":
                objectInfo.name = mibFile.previousToken
                if mibFile.getToken(" \t\n\r\{\(") == "LAST-UPDATED":
                    objectInfo.parentName = mibFile.findToken("::=", " \t\n\r\{\(")
                    objectInfo.branch = mibFile.getToken(" \t\n\r}\)")
                    self._objectList.append(objectInfo)
                    objectInfo = _MibObject()
                
            elif mibFile.token == "OBJECT-IDENTITY":
                objectInfo.name = mibFile.previousToken
                if mibFile.getToken(" \t\n\r\{\(") == "STATUS":
                    objectInfo.parentName = mibFile.findToken("::=", " \t\n\r\{\(")
                    objectInfo.branch = mibFile.getToken(" \t\n\r}\)")
                    self._objectList.append(objectInfo)
                    objectInfo = _MibObject()

            elif mibFile.token == "TEXTUAL-CONVENTION":
                tcName = mibFile.previousToken
                if mibFile.getToken(" \t\n\r\{\(") != "STATUS":
                    if mibFile.token != "DISPLAY-HINT": continue
                mibFile.findToken("SYNTAX", " \t\n\r\{\(")
                tcType = mibFile.token
                if self._objectTypes.has_key(tcType):
                    tcType = self._objectTypes[tcType]
                else:
                    tcType = ""
                self._tcDict[tcName] = tcType

                if mibFile.token == "INTEGER":
                    if mibFile.getToken(" \t\n\r\(:") == "{":
                        while mibFile.token != "}":
                            if mibFile.getToken(" \t\n\r\(:") == "--":
                                mibFile.getToken("\t\n\r");
                            else:
                                mibFile.getToken(" \t\n\r\(\):");
                                if mibFile.getToken(" \t\n\r\):") != ",": break
        mibFile.close()
        
    def _buildOidDictionary(self):
        """
        Processes the list of MIB objects and creates a dictionary of object OIDs
        """
        #Search for the parent of each node, and store the list index of the parent item
        for child in self._objectList:
            if child.branch == "org":
                child.branch = "1"
            if child.parentName:
                for parent in self._objectList:
                    if parent.name == child.parentName:
                        child.parent = parent
                        break

        #Now create an OID for each object by concatenating all ancestor branch numbers
        self._objectDict.clear()
        for leaf in self._objectList:
            leaf.oid = leaf.branch
            parent = leaf.parent
            while parent:
                #leaf.oid = parent.branch + "." + leaf.oid
                #parent = parent.parent
                if not parent.oid:
                    #Keep iterating to build up the OID one number at a time
                    leaf.oid = parent.branch + "." + leaf.oid
                    parent = parent.parent
                else:
                    #Parent OID already created, so rest of leaf OID is already known
                    leaf.oid = parent.oid + "." + leaf.oid
                    break
            if self._objectTypes.has_key(leaf.syntax):
                leaf.syntax = self._objectTypes[leaf.syntax]
            elif self._tcDict.has_key(leaf.syntax):
                leaf.syntax = self._tcDict[leaf.syntax]
            self._objectDict[leaf.name.lower()] = (leaf.oid, leaf.syntax)

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"


#