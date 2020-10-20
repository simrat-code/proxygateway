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

banner_text = " Proxy Gateway "

def menu():
    print("\t"+ "=" * (8 + len(banner_text) + 8))
    print("\t"+ "+"*8 + banner_text + "+"*8)
    print("\t"+ "=" * (8 + len(banner_text) + 8))
    print("")
    print("\t 1 - start server")
    print("\t 2 - stop server")
    print("\t 3 - status check")
    print("\t 0 - exit")
    print("")
    choice = input("enter choice: ")
    return choice


def cleanup_server(thr):
    print("[=] waiting for server-thread to complete...")
    if thr:
        event.set()
        # wait for 'server' thread to exit
        thr.join()
        thr = None
        event.clear()
        print("[=] server cleanup done")


def menu_block(proxy_server_thread, event):
    choice = menu()
    if choice == "1": 
        # start server
        if proxy_server_thread is None:
            proxy_server_thread = server_thread.ServerProxyGW(event)
            proxy_server_thread.start()

            # wait for server to start-up
            event.wait()
            event.clear()
        else:
            print("server already running")        
    elif choice == "2" or choice == "0":
        # stop server
        # need to set threading.Event()
        cleanup_server(proxy_server_thread)
        proxy_server_thread = None 
    elif choice == "3":
        if proxy_server_thread: 
            print("server is running")
        else: 
            print("server is not running")
    else:
        print("invalid choice")
    return choice


if __name__ == "__main__":

    if sys.version_info.major != 3:
        raise Exception("Must use Python 3.x")

    proxy_type = ProxyType.direct
    proxy_server_thread = None
    event = threading.Event()
    
    try:
        while True:
            choice = menu_block(proxy_server_thread, event)
            print(choice)
            if choice == "0": break

    except KeyboardInterrupt as e:
        print("[=] user interrupt : {}".format(e))        
        cleanup_server(proxy_server_thread)
        sys.exit(1)
    
# --end--
