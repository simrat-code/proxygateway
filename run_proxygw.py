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
    import logging

    import server_thread
    import utilscode

    from client_handler import CommonClientData

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

def startup_server(pgw_thread, ccd):
    ccd.eventStop.clear()
    if not pgw_thread.is_alive():
        pgw_thread.start()
        # wait for server to start-up
        ccd.eventStart.wait()
        ccd.eventStart.clear()
    else:
        logging.warning('server already running')
    return


def cleanup_server(pgw_thread, ccd):
    logging.warning('waiting for server-thread to complete...')
    if pgw_thread.is_alive():
        ccd.eventStop.set()
        # wait for 'server and client' thread while-loop to exit
        pgw_thread.join()
        ccd.eventStop.clear()
        logging.info('server cleanup done')
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", help="local interface and port to listen on, eg --local 0.0.0.0:8282")
    parser.add_argument("--parent", help="parent proxy interface and port, eg --parent 10.0.0.22:8080")
    args = parser.parse_args()

    logging.basicConfig(
        level = logging.INFO,
        format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )
    utilscode.banner()
    ccd = CommonClientData()

    # An event object manages an internal flag that can be 
    # set()     : set flag to true
    # clear()   : reset the flag to false
    # wait()    : blocks until the flag is true.
    ccd.eventStart = threading.Event()
    ccd.eventStop = threading.Event()
    pgw_thread = server_thread.ServerProxyGW(ccd)

    try:
        if args.local:
            pgw_thread.addr, pgw_thread.port = utilscode.fetchAddressPort(args.local)
        if args.parent:
            ccd.paddr, ccd.pport = utilscode.fetchAddressPort(args.parent)
                
        startup_server(pgw_thread, ccd)
        while pgw_thread.is_alive(): time.sleep(5)
        logging.error('server exited unexpectedly')

    except KeyboardInterrupt as e:
        logging.info('user interrupt: {e}')
        sys.exit(1)
    except ValueError as e:
        logging.error('Exception: invalid argument provided')
    finally:
        cleanup_server(pgw_thread, ccd)
    
# --end--
