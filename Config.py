#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/System/Config.py,

"""
Configuration Module
Provides the ability to load and save configuration files (in the Windows ini format)
"""
__docformat__ = 'epytext en' #Formatted for use with Epydoc tool (http://epydoc.sourceforge.net/)

import ConfigParser
import string

#Default configuration settings. Options overridden by those read from a file.
_defaultConfig = {}

def loadConfig(file):
    """
    Returns a dictionary with key's of the form <section>, and the values are
    another dictionary with key <option> and values from the specified ini file.

    @type  file: string
    @param file: Name of ini file to load configuration from.
    @rtype: dict
    @return: Dictionary containing the configuration information.
    """
    config = _defaultConfig.copy()
    parser = ConfigParser.ConfigParser()
    parser.read(file)
    for section in parser.sections():
        config[section] = {}
        for option in parser.options(section):
            value = string.strip(parser.get(section, option))
            config[section][option] = value
    return config

def saveConfig(file, config):
    """
    Saves the given dictionary as an ini file with the specified filename.

    @type  file: string
    @param file: Name of ini file to save the configuration to.
    @type  config: dict
    @param config: Disctionary conatining the configuration information to save.
    """
    f = open(file,'w')
    parser = ConfigParser.ConfigParser()
    for section in config.keys():
        parser.add_section(section)
        for option, value in config[section].items():
            parser.set(section, option, value)
    parser.write(f)
    f.close()

if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"

#

#