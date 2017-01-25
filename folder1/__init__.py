#!/usr/bin/env python
# $Header: /usr/local/cvsroot/stratex/rats/Helper/

"""
This module encapsulates commonly used functions into high level helper functions
this cuts down the complexity of the tests, and improves code maintainability

one thing to be rememeber is that the code used here can be shared amoung multiple
tests so be careful when making changes not to modify the function interfaces


__all__ = ['software',   # software loading, software reset functions
               'file',   # file operations, gunzip etc
                'nms',   # network management functions, i.e check
       'configuration',  # config functions, config.reset()
               'http',   # functions to talk to the terminals http server
                'ftp',   # functions that talk to the RATS FTP server
                'ntp',   # basic NTP server and diagnostic functions
             'telnet']


if __name__ == "__main__":
    print "RATS system support module: Cannot be run independently"


#
#
#