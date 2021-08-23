#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This source code is provided for testing/debuging purpose ;)

from nut2 import PyNUTClient
import sys

if __name__ == "__main__" :

    print( "PyNUTClient test..." )
    nut    = PyNUTClient( debug=True )
    #nut    = PyNUTClient( login="upsadmin", password="upsadmin", debug=True )

    print( 80*"-" + "\nTesting 'list_ups' :")
    result = nut.list_ups( )
    print( "\033[01;33m%s\033[0m\n" % result )

    print( 80*"-" + "\nTesting 'list_vars' :")
    result = nut.list_vars( "dummy" )
    print( "\033[01;33m%s\033[0m\n" % result )

    print( 80*"-" + "\nTesting 'list_commands' :")
    result = nut.list_commands( "dummy" )
    print( "\033[01;33m%s\033[0m\n" % result )

    print( 80*"-" + "\nTesting 'list_rw_vars' :")
    result = nut.list_rw_vars( "dummy" )
    print( "\033[01;33m%s\033[0m\n" % result )

    print( 80*"-" + "\nTesting 'run_command' (Test front panel) :")
    try :
        result = nut.run_command( "UPS1", "test.panel.start" )
    except :
        result = sys.exc_info()[1]
    print( "\033[01;33m%s\033[0m\n" % result )

    print( 80*"-" + "\nTesting 'set_var' (set ups.id to test):")
    try :
        result = nut.set_var( "UPS1", "ups.id", "test" )
    except :
        result = sys.exc_info()[1]
    print( "\033[01;33m%s\033[0m\n" % result )
