
import threading
import socket
import select
import sys
import time
import logging

from client_handler import ClientHandlerThread


class ServerProxyGW(threading.Thread):

    def __init__(self, ccd):
        super().__init__(name="Server-0")
        self._port = 8282
        self._addr = '0.0.0.0'
        self._ccd = ccd

    def run(self):
        try:
            sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock_server.bind((self._addr, self._port))
        except OSError as e:
            logging.warning(f'Exception Caught: {e}')
            logging.warning('unable to start server')
            # send signal to main thread
            self._ccd.eventStart.set()
            return
        sock_server.listen(5)
        sock_server.setblocking(False)
        # printMsg("server started on {}:{}".format(self._addr, self._port), nl=True)
        logging.info("server started on {}:{}".format(self._addr, self._port))

        # send 'up' status to main thread
        self._ccd.eventStart.set()

        id = 0
        inputs = []
        outputs = []

        inputs.append(sock_server)
        while not self._ccd.eventStop.is_set():
            # timeout field has been set as on Windows during select() prog
            # do respond to Ctrl+C
            # It is after timeout it accept 'pending' user interrupt
            readable, _, _ = select.select (inputs, outputs, inputs, 5)
            for s in readable:
                if s is sock_server:
                    id = id + 1
                    # printMsg("accepting new request", id=id)
                    logging.info("accepting new request")
                    sock_client, addr = s.accept()
                                        
                    # starting a new client thread
                    # and 'event_stop' to indicate application exit.
                    ClientHandlerThread(id, sock_client, addr, self._ccd).start()
        else:
            # condition in while-loop is not satisfied
            if (sock_server):
                sock_server.close()
            logging.info("server socket closed")
    
    @property
    def port(self): return self._port
    @port.setter
    def port(self, value): self._port = int(value)

    @property
    def addr(self): return self._addr
    @addr.setter
    def addr(self, value): self._addr = value
