#
# Author    : Simrat Singh
# Date      : May-2020
#

import logging


class CommonThreadData():
    def __init__(self):
        self._event_start = None
        self._event_stop = None
        self._paddr = ''
        self._pport = -1

    @property
    def eventStart(self): return self._event_start
    @eventStart.setter
    def eventStart(self, value): self._event_start = value

    @property
    def eventStop(self): return self._event_stop
    @eventStop.setter
    def eventStop(self, value): self._event_stop = value

    @property
    def paddr(self): return self._paddr
    @paddr.setter
    def paddr(self, value): self._paddr = value

    @property
    def pport(self): return self._pport
    @pport.setter
    def pport(self, value): self._pport = int(value)


def startServer(pgw_thread, ctd):
    ctd.eventStop.clear()
    if pgw_thread.is_alive():
        logging.warning('server already running')
        return
    pgw_thread.start()
    # wait for server to start-up
    ctd.eventStart.wait()
    ctd.eventStart.clear()    


def cleanServer(pgw_thread, ctd):
    logging.warning('waiting for server-thread to complete...')
    if not pgw_thread.is_alive():
        return
    ctd.eventStop.set()
    # wait for 'server and client' thread while-loop to exit
    pgw_thread.join()
    ctd.eventStop.clear()
    logging.info('server cleanup done')


def printDataRate(str_data, id=0, end_char='', on_newline=True):
    leading_newline = '\r'
    print("{}[{:03d}] {}".format(leading_newline, id, str_data), end=end_char, flush=True )


def fetchAddressPort(text):
    '''Return tuple(address, port)
    raise ValueError if separation char ie ':' not found
    '''
    pos = text.find(':')
    if pos == -1: raise ValueError
    address = text[:pos]
    port = text[pos+1:]
    if not port or not address: raise ValueError
    return (address, port)


def banner():
    text = " Proxy Gateway "
    print(" "*4 + "="*(16 + len(text)))
    print(" "*4 + "+"*8 + text + "+"*8)
    print(" "*4 + "="*(16 + len(text)))
    print("")