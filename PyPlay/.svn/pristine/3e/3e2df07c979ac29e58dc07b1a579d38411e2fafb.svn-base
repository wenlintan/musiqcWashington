
import socket, select, sys
sys.path.append('/home/crazedfool/lib/python')

from client import TLockClient
from serial2tcp import Redirector
from file_api import FileParameterClient
from json_api import JSONAPIRequestHandler, JSONAPIServer

if __name__ == "__main__":
    COM = "COM8"
    BAUD = 19200

    HOST = 'localhost' #'172.28.189.202'
    PORT = 7777

    DATA_FILE = "data.txt"
    VALUE_FILE = "newvals.txt"
    
    redir = Redirector.start_process(COM, BAUD, PORT)
    tlock = TLockClient.TCP(HOST, PORT)
    server = JSONAPIServer(('', 8321), JSONAPIRequestHandler, tlock)
    param_client = FileParameterClient( VALUE_FILE )

    param_client.start()	
    while True:
        try:
            r, w, e = select.select([tlock, server], [], [], 1)
            for ri in r:
                ri.handle_request()
        except socket.error, msg:
            sys.stderr.write("[ERROR] %s\n" % msg[1])
            sys.exit(3)
        except KeyboardInterrupt:
            break

    param_client.stop()
    Redirector.stop_process( redir )

