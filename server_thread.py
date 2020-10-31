
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
        self._port = 8282
        self._addr = '0.0.0.0'

    def run(self):
        sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock_server.bind((self._addr, self._port))
        sock_server.listen(5)
        sock_server.setblocking(False)
        printMsg("server started on {}:{}".format(self._addr, self._port), on_newline=True)

        # send 'up' status to main thread
        self.event_start.set()

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
            print("[=] server socket closed")
    
    @property
    def port(self): return self._port

    @port.setter
    def port(self, p): self._port = p

    @property
    def addr(self): return self._addr

    @addr.setter
    def addr(self, a): self._addr = a
