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
    print("\t"+ "+"*8 +"Proxy Gateway"+ "+"*8)
    print("\t 1 - start server")
    print("\t 2 - stop server")
    print("\t 0 - exit")
    print("")
    choice = input("enter choice: ")
    return choice


if __name__ == "__main__":

    if sys.version_info.major != 3:
        raise Exception("Must use Python 3.x")

    proxy_type = ProxyType.direct
    proxy_server_thread = None
    event = threading.Event()
    
    

    while True:
        choice = menu()

        if choice == "1": 
            # start server
            if proxy_server_thread is None:
                proxy_server_thread = server_thread.ServerProxyGW(event)
                proxy_server_thread.start()
            else:
                print("server already running")
            
        elif choice == "2" or choice == "0":
            # stop server
            # need to set threading.Event()
            if proxy_server_thread:
                event.set()
                proxy_server_thread.join()
                proxy_server_thread = None
                event.clear()

            if choice == "0":
                break
        
        else:
            pass

    
# --end--
