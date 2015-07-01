from socket import *

class Packet:
    trans = {}
    for x in range(256):
        trans[chr(x)] = x

    HELO = 'a'
    TALK = 'b'
        
    def __init__(self, data = ""):
        if not len(data):
            self.d = ""     #can't use default value, only one exists
        else:
            self.d = data
        self.pos = 0

    def write_int(self, num):
        s = ''.join([chr((x >> (i*8))%256) for i in range(4)])
        self.d += data
        return self

    def read_int(self):
        t = Packet.trans
        d = self.d

        self.pos += 4
        return sum([t[x[i]] << (i*8) for i in range(self.pos-4, self.pos)])

    def write_string(self, string):
        self.write_int( len(string) )
        self.d += string
        return self

    def read_string(self):
        l = self.read_int()
        s = self.d[ pos: pos+l ]
        pos += l
        return s

    def write_type(self, t):
        self.d += t
        

class Network:
    def __init__(self):
        self.handle = {}

    def receive(self):
        data = ""
        newdata = self.s.recv(5012)
        
        while len(newdata):
            data += newdata
            newdata = self.s.recv(5012)
            
        while len(data):
            try:
                used = self.handle[0] (data[1:])
                data = data[:used]
            except KeyError:
                print "Unknown packet type."
            

    def send(self, data):
        self.s.send(data)

    

class Client (Network):
    def __init__(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.connect(('localhost', 17239))
        self.s.setblocking(False)

    def __del__(self):
        self.s.close()
    
        
        
