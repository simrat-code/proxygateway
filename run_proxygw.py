#
# Author    : Simrat Singh
# Date      : Apr-2020
#


import time
import enum
import sys
import socket
import threading

import server_thread

"""
https://null-byte.wonderhowto.com/how-to/sploit-make-proxy-server-python-0161232/

Types of Proxy:
1) PHP Proxy
2) CGI Proxy
3) HTTP Proxy
4) Gateway Proxy    <== [the one implementing here]
5) DNS Proxy
6) Anonymous HTTPS Proxy
7) Suffix Proxy
8) TOR Proxy
9) I2P Anonymous Proxy

https://www.geeksforgeeks.org/creating-a-proxy-webserver-in-python-set-1/

"""

class ProxyType(enum.Enum):
    direct = 1
    proxy = 2


def menu():
    banner_text = " Proxy Gateway "

    print("\t"+ "=" * (8 + len(banner_text) + 8))
    print("\t"+ "+"*8 + banner_text + "+"*8)
    print("\t"+ "=" * (8 + len(banner_text) + 8))
    print("")
    print("\t 1 - start server")
    print("\t 2 - stop server and exit")
    print("\t 3 - status check")
    print("\t 0 - exit")
    print("")
    choice = input("enter choice: ")
    return choice


def cleanup_server(pgw_thread, event_stop):
    print("[=] waiting for server-thread to complete...")
    if pgw_thread.is_alive():
        event_stop.set()
        # wait for 'server and client' thread-while to exit
        pgw_thread.join()
        # event_stop.clear()
        print("[=] server cleanup done")


def menuBlock(pgw_thread, event_start, event_stop):
    choice = menu()
    if choice == "1": 
        # start server
        event_stop.clear()
        if not pgw_thread.is_alive():
            pgw_thread.start()
            # wait for server to start-up
            event_start.wait()
            event_start.clear()
        else:
            print("server already running")        
    elif choice == "2" or choice == "0":
        # stop server and set exit flag
        # by assigning zero to choice
        # It is required since server run as thread and once
        # joined/complete should not call run() method again
        cleanup_server(pgw_thread, event_stop)
        choice = "0"
    elif choice == "3":
        var = "" if pgw_thread.isRunning() else "not "
        print("server is {}running".format(var))
    else:
        print("invalid choice")
    return choice


if __name__ == "__main__":

    if sys.version_info.major != 3:
        raise Exception("Must use Python 3.x")

    proxy_type = ProxyType.direct
    # An event object manages an internal flag that can be 
    # the set() method  : set flag to true
    # the clear() method: reset the flag to false
    # the wait() method : blocks until the flag is true.
    event_start = threading.Event()
    event_stop = threading.Event()
    proxy_server_thread = server_thread.ServerProxyGW(event_start, event_stop)
    
    try:
        while True:
            choice = menuBlock(proxy_server_thread, event_start, event_stop)
            print(choice)
            if choice == "0": break

    except KeyboardInterrupt as e:
        print("[=] user interrupt : {}".format(e))        
        cleanup_server(proxy_server_thread, event_stop)
        sys.exit(1)
    
# --end--
