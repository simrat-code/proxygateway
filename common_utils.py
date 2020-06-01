#
# Author    : Simrat Singh
# Date      : May-2020
#

import threading

#
# if prev, end_char is not newline and current line on_newline=True
# need a variable that should remember prev-value
#
def printMsg(str_data, id=0, end_char='\n', on_newline=True):
    with threading.Lock():
        leading_newline = ''
        if on_newline == True:
            printMsg.prev_end_char = getattr(printMsg, 'prev_end_char', '\n')
            if printMsg.prev_end_char != '\n':
                leading_newline = '\n'
        else:
            leading_newline = '\r'
        printMsg.prev_end_char = end_char
        print("{}[{:03d}] {}".format(leading_newline, id, str_data), end=end_char, flush=True )