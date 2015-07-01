import socket

class Network:
    OPEN_GAMES = 1
    CREATE = 2
    JOIN = 3
    POS = 4
    ROT = 5
    FIRE = 6
    
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.addr = socket.gethostbyaddr(host)
        self.port = port

    def server(self):
        self.sock.connect(self.addr[0], self.port)
        self.sock.send( socket.htonl(self.OPEN_GAMES) )
        data = self.sock.recv(4098)

        games = data.split("|")
        parsed_games = []

        for x in range( len(games) ):
            new_game = [ int(ntohl( games[x][0:4] )) ]   #host
            new_game.append( int(ntohs( games[x][4:6]) ) #port
            new_game.append( int(ntohs( games[x][6:8]) ) # numplayers

            strlen = ntohs( games[x][8:10] )
            new_game.append( games[x][10: 10 + strlen] )
            parsed_games.append(new_game)

        self.sock.close()
        return parsed_games

    def join(self, num):
        self.sock.connect(self.addr[0], self.port)
        self.sock.send( socket.htonl(self.OPEN_GAMES)+ socket.htonl(num) )
        data = self.sock.recv(32)

        ip = int( socket.ntohl(data[0:4]) )
        port = int( socket.ntohs(data[4:6]) )

        del self.sock
        self.sock.connect(ip, port)
        

    def update(self, pos):
        string = ""
        for x in range(2):
            whole = int(pos[x])
            frac = pos[x] - int(pos[x])
            frac = int( frac * 1000000.0 )

            string += socket.htonl(whole) + socket.htonl(frac)

        
            
