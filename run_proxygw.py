#
# Author    : Simrat Singh
# Date      : Apr-2020
#


import time
import enum
import sys
import socket
import threading
import argparse

import server_thread
import utilscode

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


def banner():
    banner_text = " Proxy Gateway "

    print(" "*4 + "=" * (8 + len(banner_text) + 8))
    print(" "*4 + "+"*8 + banner_text + "+"*8)
    print(" "*4 + "=" * (8 + len(banner_text) + 8))
    print("")


def startup_server(pgw_thread, event_start, event_stop):
    event_stop.clear()
    if not pgw_thread.is_alive():
        pgw_thread.start()
        # wait for server to start-up
        event_start.wait()
        event_start.clear()
    else:
        print("server already running")
    return "1"


def cleanup_server(pgw_thread, event_stop):
    print("[=] waiting for server-thread to complete...")
    if pgw_thread.is_alive():
        event_stop.set()
        # wait for 'server and client' thread-while to exit
        pgw_thread.join()
        # event_stop.clear()
        print("[=] server cleanup done")
    return "0"


if __name__ == "__main__":
    if sys.version_info.major != 3:
        raise Exception("Must use Python 3.x")

    proxy_type = ProxyType.direct
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", help="local interface and port to listen on <0.0.0.0:8282>")
    # parser.add_argument("--parent", help="parent proxy interface and port <10.0.0.22:8080>")
    args = parser.parse_args()

    try:
        banner()
        # An event object manages an internal flag that can be 
        # the set() method   : set flag to true
        # the clear() method : reset the flag to false
        # the wait() method  : blocks until the flag is true.
        event_start = threading.Event()
        event_stop = threading.Event()
        pgw_thread = server_thread.ServerProxyGW(event_start, event_stop)

        if args.local:
            value = utilscode.fetchAddressPort(args.local)
            pgw_thread.addr = value[0]
            pgw_port = value[1]
        
        startup_server(pgw_thread, event_start, event_stop)
        pgw_thread.join()

    except KeyboardInterrupt as e:
        print("\n[-] user interrupt : {}".format(e))
        sys.exit(1)
    except ValueError as e:
        print("[-] Exception Caught: invalid argument provided")
    finally:
        cleanup_server(pgw_thread, event_stop)
    
# --end--
