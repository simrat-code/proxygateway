#
# Author    : Simrat Singh
# Date      : May-2020
#

import threading

#
# if prev, end_char is not newline and current line on_newline=True
# need a variable that should remember prev-value
# 
# for printing two types;
#   - simple messages (simple)
#   - data rate (dr)
#

def printMsg(str_data, id=0, nl=True):
    with threading.Lock():
        start_char = ''
        if nl == True:
            start_char = '\n'
        else:
            start_char = '\r'
        print("{}[{:03d}] {}".format(start_char, id, str_data), end='', flush=True )


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
    banner_text = " Proxy Gateway "
    print(" "*4 + "="*(16 + len(banner_text)))
    print(" "*4 + "+"*8 + banner_text + "+"*8)
    print(" "*4 + "="*(16 + len(banner_text)))
    print("")