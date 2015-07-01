import socket

class Server:
    OPEN_GAMES = 1
    CREATE = 2
    JOIN = 3
    POS = 4
    ROT = 5
    FIRE = 6
    
    games = []
    clients = []

    def __init__(self):
        self.run()

    def run(self):
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.sock.bind(('', 8821))
        self.sock.listen(5)

        while True:
            newsock, addr = sock.accept()
            print "got: ", addr

            data = newsock.recv(1024)
            
