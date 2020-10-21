
import threading
import socket
import select
import sys
import time

from client_handler import ClientHandlerThread
from utilscode import printMsg

class ServerProxyGW(threading.Thread):

    def __init__(self, event_start, event_stop):
        super().__init__()
        self.event_start = event_start
        self.event_stop = event_stop

        self.max_connection = 5
        self.buf_size = 8192
        self.port = 8282
        self.status = False

    def run(self):
        sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock_server.bind(('', self.port))
        sock_server.listen(self.max_connection)
        sock_server.setblocking(False)
        printMsg("server started successfully on port {}".format(self.port), on_newline=True)

        # send 'up' status to main thread
        self.event_start.set()
        self.status = True

        id = 0
        inputs = []
        outputs = []

        inputs.append(sock_server)
        while not self.event_stop.is_set():
            # timeout field has been set as on Windows during select() prog
            # do respond to Ctrl+C
            # It is after timeout it accept 'pending' user interrupt
            readable, writable, exceptional = select.select (inputs, outputs, inputs, 5)
            for s in readable:
                if s is sock_server:
                    id = id + 1
                    printMsg("accepting new request", id=id)
                    sock_client, addr = s.accept()
                                        
                    # starting a new client thread
                    # and 'event_stop' to indicate application exit.
                    ClientHandlerThread(self.event_stop, id, sock_client, addr).start()
        else:
            if (sock_server):
                sock_server.close()
            self.status = False
            print("[=] server socket closed")

