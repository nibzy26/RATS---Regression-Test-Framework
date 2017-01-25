#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/System/RestoreConfig.py,

"""
   Script : Restore Rats configuration

   Description: Restores all RATS terminals to the default configuration, that is all terminals
                set-up with plug-ins configured and a working radio link between them
                                   
   Requirements: All terminals must be accessable by IP address
"""

#--------------------------------------------------------------------------
# imports
#--------------------------------------------------------------------------
import time
from   Modules import Timer
import httplib
import StringIO
import shlex
from   Snmp import SnmpManager
from   SysLog import SysLog
from   threading import Thread
import re
from   Helper import *

#
#
#
class RestorerThread(Thread):
    
   def __init__ (self, node):
      Thread.__init__(self)
      self.node = node
      self.ipAddress = node.address
      self.exitStatus = False
      #print "RestorerThread *****", self.ipAddress
      
   #----------------------------------------------------------------------
   # Restore previously stored config
   #----------------------------------------------------------------------      
   def run(self):

      # temp storage for capacity/modulation
      caps = []
      mods = []
      
      fileName = 'cfg-active//'+self.ipAddress+'-cfg-active'

      try:
          cfgstream = open( fileName, 'rt')
      except IOError:
          print 'failed to open file', fileName
          self.exitStatus = False
    
      # count lines in file (could do this with readlines)
      lines = 0
      for line in cfgstream:
          lines += 1


      configuration.reset( self.node )
      
      self.node.resetConfig() 
      # set inactive context
      #-------------------------------------------------------------------- 
      cfgstream.seek(0)

      # parse configuration, and restore by SNMP/PTI interface
      count = 0
      for line in cfgstream:
         
          splitLine = shlex.split(line)
          
          count += 1

          if splitLine[0] == 'contextid':
              self.node.community = splitLine[1].lower()
              continue
              
          if splitLine[0] == 'set':
             #splitLine.append('')

             if len(splitLine) < 4:
                continue

             # store capacity and modulation settings for each
             # slot, this is to get around a bug in the terminal
             # where the capacity is not set
             if str(splitLine[1]).find('unityRmConfigCapacity') != -1:
                caps.append((self.node.community, splitLine[3]))

             if str(splitLine[1]).find('unityRmConfigModemModulation') != -1:
                mods.append((self.node.community, splitLine[3]))
                
             # don't reboot
             if str(splitLine[1]).find('swManagerSoftReset') != -1:
                continue

             # ignore save, we will manage this manually
             if str(splitLine[1]).find('configCommit') != -1:
                continue                   

             instance = splitLine[2]
             value    = splitLine[3]

             if len(value):             
                #print splitLine
                #self.node.pti_set(splitLine[1], instance, value)
                self.node.set(splitLine[1], instance, value)
             #else:
             #   print 'ignoring', splitLine

      # advice from portal team is to wait before we do a commit for
      # the terminal to catch up.. lets see how we go
      Timer.Wait("Waiting for node to catch up", 40)

      # commit!
      self.node.activateConfig()

      # software reset?
      software.reset(self.node, ignoreAlarms=True)

      self.exitStatus = True        
      
      #
      # the following code is an attempt to toggle to capacity on all errored
      # RACS, this should get around what seems to be a bug with setting the capacity
      # after a restore.
      
      #Timer.Wait("Wait to do capacity toggle (flush), **work around**", 20)
                 
      # do a capacity toggle, ?
      #for cap in caps:
      #   self.node.community = cap[0]
      #   self.node.set('unityRmConfigCapacity', 0, 0 )
         
      #for mod in mods:
      #   self.node.community = mod[0]
      #   self.node.set('unityRmConfigModemModulation', 0, 0 )

      #self.node.activateConfig()

      #Timer.Wait("Wait to do capacity toggle (restore), **work around**", 20)
  
      # do a capacity toggle, ?
      #for cap in caps:
      #   self.node.community = cap[0]
      #   self.node.set('unityRmConfigCapacity', 0, cap[1] )
      #   
      #for mod in mods:
      #   self.node.community = mod[0]
      #   self.node.set('unityRmConfigModemModulation', 0, mod[1] )
         
         
      #self.node.activateConfig()      
      
              

         
#

#
