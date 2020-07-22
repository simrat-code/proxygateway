
import threading
import socket
import select
import sys
import os

from client_handler import ClientHandlerThread
from common_utils import printMsg

class ServerProxyGW(threading.Thread):

    def __init__(self, event):
        super().__init__()
        self.event = event

        self.max_connection = 5
        self.buf_size = 8192
        self.port = 8282

    def run(self):
        try:
            sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if os.name == "posix":
                sock_server.setsockopt(SO_REUSEADDR, 1)   # for POSIX only
                
            sock_server.bind(('', self.port))
            sock_server.listen(self.max_connection)
            sock_server.setblocking(False)
            printMsg("server started successfully on port {}".format(self.port), on_newline=True)

            id = 0
            inputs = []
            outputs = []

            inputs.append(sock_server)
            while not self.event.is_set():
                #print("[=] waiting for new request")
                #
                # timeout field has been set as on Windows during select() prog
                # do respond to Ctrl+C
                # It is after timeout it accept 'pending' user interrupt
                #
                readable, writable, exceptional = select.select (inputs, outputs, inputs, 5)
                for s in readable:
                    if s is sock_server:
                        id = id + 1
                        printMsg("accepting new request", id=id)
                        sock_client, addr = s.accept()
                        
                        #
                        # starting a new thread
                        #
                        ClientHandlerThread(self.event, id, sock_client, addr).start()

        except KeyboardInterrupt as e:
            print("[=] user interrupt : {}".format(e))
            sys.exit(1)

        finally:
            if (sock_server):
                sock_server.close()
                sock_server = None
                print("[=] server socket closed")



