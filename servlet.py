import socket
import sys
import struct

class Servlet:
    def __init__(self,port,file,list):
        self.port = port
        self.keyval = process_dict_file(file)

        def process_dict_file(self,file):
            #creates a dict from the key-value file
            f_dict = {}

            return f_dict
    def frame_message(type,msg=''):
        '''
        Creates framed messages
        Numbers are bytes.
        Protocol is defined as:
        KeyReq (type = 5)
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

        return frame

    def run():
        pass

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 3:
        print('Wrong number of args')
        sys.exit(0)
    else:
        port = int(sys.argv[1])
        file = sys.argv[2]
        #TODO implement parsing of ip:ports
        servlet = Servlet(port,file)
        servlet.run()
