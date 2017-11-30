import socket
import sys
import struct

class Servent:
    def __init__(self,port,file,list=[]):
        self.port = port
        self.keyval = self.process_dict_file(file)
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.bind(("",port))
        self.TTL = 3
        self.recent_wind = []


    def process_dict_file(self,file):
        #creates a dict from the key-value file
        f_dict = {}
        with open(file,'r') as fp:
            #reads lines from dict file
            #gets pair key-value and inserts in f_dict
            line = fp.readline()
            while(line):
                if line[0] == '#':
                    line = fp.readline()
                    continue
                pair = line.split(None,1)
                f_dict[pair[0]] = pair[1][:-1]
                line = fp.readline()
        return f_dict

    def frame_message(self,type_msg,seqnum,origip=0,origport=0,msg=''):
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
        frame += struct.pack('!H',type_msg)
        if type_msg == 7 or type_msg == 8:
            frame += struct.pack('!H',self.TTL)
        frame += struct.pack('!I',seqnum)
        if type_msg == 7 or type_msg ==8:
            frame += struct.pack('!I',origip)
            frame += struct.pack('!H',origport)
        if type_msg == 9:
            frame += struct.pack('!I',seqnum)
        frame += msg.encode()
        return frame

    def run(self):
        while True:
            rcv = self.socket.recvfrom(420)
            msg = rcv[0]
            sender_ip = rcv[1][0]
            sender_port = rcv[1][1]
            type_msg = struct.unpack('!H',msg[0:2])[0]
            # print(type_msg)
            if type_msg == 5 :
                print('bacana')
                nseq = struct.unpack('!I',msg[2:6])[0]
                info = msg[6:].decode()
                self.create_key_flood(nseq,sender_ip,sender_port,info)
                print(info,info in self.keyval)
                if info in self.keyval:
                    self.send_answer(nseq,info,sender_ip,sender_port)
            if type_msg == 6:
                nseq = struct.unpack('!I',info[2:6])[0]
            if type_msg == 7 or type_msg ==8:
                TTL = msg[2:4]
                nseq = struct.unpack('!I',msg[4:8])[0]
                ip = struct.unpack('!I',msg[8:12])[0]
                port = struct.unpack('!H',msg[12:14])[0]
                info = msg[14:].decode()
                if type_msg == 7:
                    if nseq not in self.recent_window:
                        self.new_message(nseq)
                        if info in self.keyval:
                            self.send_answer(nseq,info,ip,port)
                    #TODO flood msg to contacts
            print(msg)

    def new_message(self,nseq):
        recent_window.append(nseq)
        if len(recent_window) > 30:
            recent_window = recent_window[1:]


    def ip_b_str(self,ip):
        '''
            convert ip bytes to str
        '''
        return str(ip[0]) + '.' + str(ip[1])+ '.' + str(ip[2])+ '.' + str(ip[3])

    def ip_str_b(self,ip):
        print(ip,'ip')
        byte_str = bytes()
        for i in ip.split('.'):
            byte_str += struct.pack('!B',int(i))
        return byte_str

    def send_answer(self,seqnum,msg,ip,port):
        frame = self.frame_message(9,seqnum,msg)
        print('frame')
        print(msg)
        print(frame)
        self.socket.sendto(frame,(ip,port))

    def create_topo_flood(self,seqnum,ip,port,msg):
        frame = self.frame_message(7,seqnum,ip,port,self.keyval[msg])

    def create_key_flood(self,seqnum,ip,port,msg):
        frame = self.frame_message(6,seqnum,ip,port,msg)

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 3:
        print('Wrong number of args')
        sys.exit(0)
    else:
        port = int(sys.argv[1])
        file = sys.argv[2]
        #TODO implement parsing of ip:ports
        servent = Servent(port,file)
        print(servent.keyval)
        servent.run()
