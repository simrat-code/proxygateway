#
# Author    : Simrat Singh
# Date      : Apr-2020
#

import sys

try:
    if sys.version_info.major != 3: raise NameError

    import time
    import socket
    import threading
    import argparse

    import server_thread
    import utilscode

except NameError as e:
    print("[-] Exception Caught: Must use Python 3.x")
    sys.exit(1)

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", help="local interface and port to listen on <0.0.0.0:8282>")
    # parser.add_argument("--parent", help="parent proxy interface and port <10.0.0.22:8080>")
    args = parser.parse_args()

    utilscode.banner()
    # An event object manages an internal flag that can be 
    # set()     : set flag to true
    # clear()   : reset the flag to false
    # wait()    : blocks until the flag is true.
    event_start = threading.Event()
    event_stop = threading.Event()
    pgw_thread = server_thread.ServerProxyGW(event_start, event_stop)

    try:
        if args.local:
            pgw_thread.addr, pgw_thread.port = utilscode.fetchAddressPort(args.local)
        
        startup_server(pgw_thread, event_start, event_stop)
        while pgw_thread.is_alive(): time.sleep(5)
        print("[x] server thread exited unexpectedly")

    except KeyboardInterrupt as e:
        print("\n[-] user interrupt : {}".format(e))
        sys.exit(1)
    except ValueError as e:
        print("[-] Exception Caught: invalid argument provided")
    finally:
        cleanup_server(pgw_thread, event_stop)
    
# --end--
