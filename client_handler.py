#
# Author    : Simrat Singh
# Date      : Apr-2020
#

import threading
import socket
import select
import time
import logging


def nextValueOf(text, src_list):
    print(src_list)
    x = len(src_list)
    flag = 0
    for i in range(x):
        if (flag == 1): return src_list[i]
        #
        # pattern found, now need to return the next value
        # set flag to return on next value
        #
        if (src_list[i] == text): flag = 1      
    raise ValueError


def portForService(protocol):
    if ("http" == protocol):
        return 80
    elif ("https" == protocol):
        return 443
    else:
        return 80
  

class ClientHandlerThread(threading.Thread):
    static_resp = ("HTTP/1.0 200 OK \r\n"
            "Date: Thu, 14 Mar 2019 16:28:53 GMT\r\n"
            "Server: Apache/2.2.14 (Win32)\r\n"
            "Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT\r\n"
            "Content-Length: 0\r\n"
            "Content-Type: text/html\r\n"
            "\r\n")


    def __init__(self, thread_id, sock_client, addr, ctd, data=""):
        super().__init__()
        self.thread_id = thread_id
        self.sock_client = sock_client
        self.addr = addr
        self.data = data
        self.ctd = ctd


    def run(self):              
        # self.sock_client.setblocking(False) # working for HTTP but error with SSL
        self.sock_client.setblocking(True)

        if not self.data:
            # no-data provided to send to webserver
            # that means, first need to recv data from client
            # for HTTPS-request this is 'CONNECT www.google.com:443 HTTP/1.1'
            data = self.sock_client.recv(8192)
            self.data = data.decode("utf-8")
        logging.debug(f'recv data len {len(self.data)}')

        try:
            self.processRequest()           
        except socket.error as e:
            logging.warning("exception occurs 01: {}".format(e))
        except ValueError as e:
            logging.warning("exception occurs 02: {}".format(e))
        except IndexError as e:
            logging.warning("exception occurs 03: {}".format(e))            
        finally:
            if (self.sock_client): 
                logging.info(f"closing client connection ----------------[ {self.name} ]")
                self.sock_client.close()
    

    def dataRateKB(self, reply):        
        dar = float(len(reply))
        dar = float(dar / 1024)
        dar = "%.3s" % (str(dar))
        dar = "%s KB" % (dar)
        return dar
    
    def fetchTarget(self, header_list):
        # check for HTTP Method in client request
        if (header_list[0] not in ["GET", "POST", "CONNECT"]):
            logging.warning("invalid HTTP method: ->{}<-".format(header_list[0]) )
            raise ValueError("invalid HTTP method")

        # item at index 1 of first-line is the webserver's or website's server address
        # CONNECT https://null-byte.wonderhowto.com:443/test.html HTTP/1.1
        # CONNECT null-byte.wonderhowto.com:443 HTTP/1.1
        url = header_list[1]

        webserver = ""
        port = -1
        protocol = "http"

        temp_index = url.find("://")
        if (temp_index != -1):
            # skip "://" and get the rest of url
            # the 'url' may be like
            # <ip-address>:<port>
            protocol = url[:temp_index]
            url = url[(temp_index + 3):]
          
        pos = url.find("/")
        index_r = len(url) if pos == -1 else pos

        index_p = url.find(":")
        if (index_p == -1):
            # do not found the port index ':' in url
            # webserver is considered upto location of '/' ie resource
            # absense of port means, either
            #   fetch from protocol if mentioned along with url ie http or https, or
            #   default 'http' ie port 80
            webserver = url[:index_r]
            port = portForService(protocol)
        else:
            # port index has been found
            # and 'index_r' will be either some value or length of url
            webserver = url[:index_p]
            port = int(url[index_p + 1:index_r] )
        return webserver, port

    def processRequest(self):
        # ============ Sample Request Format for HTTPS =============================================
        # CONNECT null-byte.wonderhowto.com:443 HTTP/1.1
        # User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0
        # Proxy-Connection: keep-alive
        # Connection: keep-alive
        # Host: null-byte.wonderhowto.com:443        
        # ==========================================================================================

        # for testing during early development - send back static resp to client
        # self.sock_client.send(self.static_resp.encode("utf-8"))
        
        logging.debug(f'parent on {self.ctd.paddr}:{self.ctd.pport}')

        first_line = self.data.split('\n')[0]
        header_list = first_line.split(' ')
        if self.ctd.paddr:
            # parent proxy is provided on command-line option
            webserver = self.ctd.paddr
            port = self.ctd.pport
        else:
            webserver, port = self.fetchTarget(header_list)

        # ignore host check
        if webserver in self.ctd.ignoreList:
            logging.info(f"ignoring: {webserver} ----") 
            return
        
        # connecting to remote server (ie destination webserver)
        # pass self.data ie original request to it
        # and send back the response to client
        logging.info("connecting: server => {}:{}".format(webserver, str(port)) )
        if (header_list[0] in ["GET", "POST"]):
            self.targetHTTPServer(webserver, port)
        elif (header_list[0] == "CONNECT"):
            self.targetSSLServer(webserver, port)
        else:
            logging.error("ALERT!!! incorrect header!!!")
            return


    def targetHTTPServer(self, webserver, port):
        try:
            sock_web = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_web.connect((webserver, port)) 
            #
            # to avoid WinError 10035:
            # "A non-blocking socket operation could not be completed immediately"
            # which occurs during sock_client.recv() call
            # so setting blocking to True ie setblocking(True)
            #
            # Solution: use select() and do setblocking(False)
            # It is normal for WSAEWOULDBLOCK to be reported as the result from 
            # calling connect on a nonblocking SOCK_STREAM socket, since 
            # some time must elapse for the connection to be established.
            #
            # another similar error:
            # WinError 10056 - socket already connected
            #
            sock_web.setblocking(False)
            sock_web.sendall(str.encode(self.data))

            inputs = [sock_web, self.sock_client]
            outputs = []
            
            self._superWhile(inputs, outputs, self.sock_client, sock_web, timeout=5)

        except socket.error as e:
            logging.warning(f"exception in targetHTTP: {e}")
        finally:
            sock_web.close()

    
    def targetSSLServer(self, webserver, port):
        #
        # https://www.ietf.org/rfc/rfc2817.txt
        # Page 5: HTTP upgrade to TLS
        #
        # Any successful (2xx) response to a CONNECT request indicates that the
        # proxy has established a connection to the requested host and port,
        # and has switched to tunneling the current connection to that server
        # connection.
        #
        # A proxy MUST NOT respond with any 2xx status code
        # unless it has either a direct or tunnel connection established to the
        # authority.
        #
        proxy_resp = "HTTP/1.1 200 Connection established\nProxy-Agent: THE Simx ProxyGateway\n\n"
        try:
            sock_web = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_web.connect((webserver, port))
            
            # to avoid WinError 10035: 
            # "A non-blocking socket operation could not be completed immediately"
            # which occurs during sock_client.recv() call
            # so setting blocking to True
            #
            # using select() as solution to above issue
            self.sock_client.setblocking(False)

            sock_web.setblocking(False)
            if self.ctd.paddr:
                # send 'CONNECT' packet to parent-proxy
                sock_web.sendall(str.encode(self.data))
            else:
                # since connection with target web-server is successful
                # Proxy should send the 2xx reply to client.
                self.sock_client.sendall(proxy_resp.encode("utf-8") )

            # now need to start the loop for handing over request-reponse
            # between client and server via proxy
            inputs = [sock_web, self.sock_client]
            outputs = []

            self._superWhile(inputs, outputs, self.sock_client, sock_web, timeout=5)
           
        except socket.error as e:
            logging.warning("exception in targetSSL: {}".format(e))
        finally:
            sock_web.close()
    

    def _superWhile(self, inputs, outputs, sock_client, sock_web, timeout=3):
        #
        # NOTE: any exception raised here will/should be caught in calling function
        #
        str_msg = ""
        end_newline = True
        select_counter = 0
        while not self.ctd.eventStop.is_set():
            ready = select.select(inputs, outputs, inputs, timeout) 
            if (not ready[0] and not ready[1] and not ready[2]): 
                select_counter += timeout
                if select_counter >= 300: 
                    logging.warning("select timeout occured")
                    break
                continue
                # break  # select timeout
            # resetting counter
            select_counter = 0
            for s in ready[0]:
                sock_recv = None
                sock_send = None

                if s is sock_client:
                    str_msg = "client --> webserver "
                    sock_recv = sock_client
                    sock_send = sock_web
                
                elif s is sock_web:
                    str_msg = "client <-- webserver "
                    sock_recv = sock_web
                    sock_send = sock_client

                else:
                    logging.warning("ALERT!!! no data, ready[0] =>{}<=".format(ready[0]))
                    time.sleep(1)
                    break

                # inputs = self.logicRecvSend(inputs, sock_recv, sock_send)
                reply = sock_recv.recv(4096)
                if (len(reply) > 0):
                    str_msg += "=> {} <=\t\t".format(self.dataRateKB(reply))
                    end_newline = False
                    sock_send.sendall(reply)                 
                else:
                    # sock_recv is done with sending data and no data will ever receive on this socket
                    str_msg += "^_^\t\t"
                    end_newline = True
                    sock_recv.shutdown(socket.SHUT_RD)
                    inputs.remove(sock_recv)
                    inputs.remove(sock_send)

                # printDataRate(str_msg, id=self.thread_id, end_char=end_char, on_newline=False)
                # printMsg(str_msg, id=self.thread_id, nl=end_newline)
                if end_newline:
                    logging.info(str_msg)
            ## end of FOR

            if not inputs: 
                #
                # if all inputs socket-descriptos are SHUT_RD
                # no need to call select(), instead exit from while-loop
                #
                break
        return
# end      