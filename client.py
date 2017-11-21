import socket
import sys
import struct

class Client:
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port

    def run(self):
        while True:
            req = input()
            if self.valid_input(req):
                print('valid input')
                if(req[0] == '?'):
                    self.req_key(req[1:])
                elif(req[0] == 'T'):
                    self.req_topo():
                else:
                    self.quit()
                continue
            else:
                print('Invalid input')
                continue

    def valid_input(self,req):
        '''
        Checks if string starts with ?, Q or T.
        Also checks if string len == 1 in Q or T.
        '''
        valid = ['?','Q','T']
        c = req[0]
        if c not in valid:
            return False
        elif c == 'Q' or c =='T':
            if len(req) == 1:
                return True
            else:
                return False
        else:
            return True

    def frame_message(msg_type,msg=''):
        '''
        Creates framed messages.
        Client can only send KeyReq and TopoReq.
        Numbers are bytes.
        Protocol is defined as:
        Req (type = 5)
        | Type | SeqNum |        Key        |
        0         2             6                  6 + length*2  
        TopoReq (type = 6)
        | Type | SeqNum |
        0         2            6
        (Key/Topo)Flood (type = 7 or 8)
        | Type| TTL | SeqNum | Orig_IP | Orig_Port |      Info        |
        0        2       4             8             12                14               14+length*2
        Answr
        | Type | SeqNum |       Key        |
        0         2             6                  6 + length*2

        Max length = 400
        '''
        frame = bytes()
        frames += struct.pack('!H',msg_type)
        frames += self.seqnum
        if msg_type == 5:
            frames += msg.encode()
        return frame

    def req_key(self,key):
        '''
            Requires key for connected node
        '''
        pass

    def req_topo(self):
        '''
            Requires topology for connected node
        '''
        pass

    def quit(self):
        '''
            Exit program
        '''
        pass

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc != 2:
        print("Wrong number of args")
        sys.exit(0)
    else:
        arg = sys.argv[1].split(':')

        if len(arg) != 2:
            print('Wrong arg')
            sys.exit(0)

        ip = arg[0]
        port = int(arg[1])

        client = Client(ip,port)
        client.run()