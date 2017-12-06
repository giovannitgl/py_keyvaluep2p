import socket
import sys
import struct
import re

class Servent:
    def __init__(self,port,file,list_con=[]):
        self.port = port
        self.keyval = self.process_dict_file(file)
        self.list_con = self.process_list(list_con)
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.bind(("",port))
        self.ip = socket.gethostbyname(socket.gethostname())
        self.TTL = 3
        self.recent_window = []
        print('IPLIST:', self.list_con)

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
                if pair[1][-1] == '\n':
                    value = pair[1][:-1]
                else:
                    value = pair[1]
                f_dict[pair[0]] = value
                line = fp.readline()
        return f_dict

    def process_list(self,list_con):
        # print('list_con',list_con)
        match = re.findall(r'(\d+.\d+.\d+.\d+|\w+):(\d+)',list_con)
        # print('match',match)
        return match
        # list_connection = []
        # for i in match:
        #     list_connection.append(i)

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
        print('frame1',frame)
        if type_msg == 7 or type_msg == 8:
            frame += struct.pack('!H',self.TTL)
            frame += struct.pack('!I',seqnum)
        # if type_msg == 7 or type_msg ==8:
            frame += self.ip_str_b(origip)
            # frame += struct.pack('!I',origip)
            frame += struct.pack('!H',origport)
        if type_msg == 9:
            frame += struct.pack('!I',seqnum)
        frame += msg.encode()
        return frame

    def run(self):
        while True:
            rcv = self.socket.recvfrom(420)
            msg = rcv[0]
            print('received msg: ',msg)
            print('from',rcv[1])
            sender_ip = rcv[1][0]
            sender_port = rcv[1][1]
            type_msg = struct.unpack('!H',msg[0:2])[0]
            # print(type_msg)
            if type_msg == 5 :
                nseq = struct.unpack('!I',msg[2:6])[0]
                info = msg[6:].decode()
                if info in self.keyval:
                    self.send_answer_key(nseq,info,sender_ip,sender_port)
                self.new_message(nseq,sender_ip,sender_port)
                flood_frame = self.create_key_flood(nseq,sender_ip,sender_port,info)
                for i in self.list_con:
                    self.socket.sendto(flood_frame,(i[0],int(i[1])))
            if type_msg == 6:
                nseq = struct.unpack('!I',msg[2:6])[0]
                new_msg = self.ip + ':' + str(self.port)
                flood_frame = self.create_topo_flood(nseq,sender_ip,sender_port, new_msg)
                self.new_message(nseq,sender_ip,sender_port)
                self.send_answer_topo(nseq,self.ip + ':' + str(self.port), sender_ip,sender_port)
                for i in self.list_con:
                    self.socket.sendto(flood_frame,(i[0],int(i[1])))
            if type_msg == 7 or type_msg ==8:
                TTL = struct.unpack('!H',msg[2:4])[0]
                nseq = struct.unpack('!I',msg[4:8])[0]
                # ip = struct.unpack('!I',msg[8:12])[0]
                ip = msg[8:12]
                port = struct.unpack('!H',msg[12:14])[0]
                info = msg[14:].decode()
                ip_str = self.ip_b_str(ip)
                if type_msg == 7:
                    if not self.received_before(nseq,ip_str,port):
                        self.new_message(nseq,ip_str,port)
                        if info in self.keyval:
                            self.send_answer_key(nseq,info,ip_str,port)
                    #TODO flood forward msg to contacts
                    self.forward_frame(msg ,TTL)
                if type_msg == 8:
                    if not self.received_before(nseq,ip_str,port):
                        print(type(nseq),type(ip_str),type(port))
                        self.new_message(nseq,ip_str,port)
                        new_info = info + ' ' + self.ip + ':' + str(self.port)
                        new_msg = msg + (' '+ self.ip + ':' + str(self.port)).encode()
                        self.send_answer_topo(nseq,new_info,ip_str,port)
                        self.forward_frame(new_msg,TTL)

            print(msg)

    def received_before(self,nseq,ip,port):
        compare = {'seq':nseq,'ip':ip,'port':port}
        for i in self.recent_window:
            if i == compare:
                return True
        return False

    def forward_frame(self,frame,TTL):
        n_ttl = TTL-1
        forward_frame = bytes()
        forward_frame += frame[0:2]
        forward_frame += struct.pack('!H',n_ttl)
        forward_frame += frame[4:]
        print('ff', forward_frame)
        if n_ttl != 0:
            for i in self.list_con:
                self.socket.sendto(forward_frame,(i[0],int(i[1])))

    def new_message(self,nseq,ip,port):
        self.recent_window.append({'seq':nseq,'ip':ip,'port':port})
        if len(self.recent_window) > 30:
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

    def send_answer_key(self,seqnum,msg,ip,port):
        # print('msg aqui',msg)
        frame = self.frame_message(9,seqnum,msg=self.keyval[msg])
        print('sending frame:',frame,'\nto',(ip,port))
        self.socket.sendto(frame,(ip,port))

    def send_answer_topo(self,seqnum,msg,ip,port):
        # print('msg aqui',msg)
        frame = self.frame_message(9,seqnum,msg=msg)
        print('sending frame:',frame,'\nto',(ip,port))
        self.socket.sendto(frame,(ip,port))

    def create_topo_flood(self,seqnum,ip,port,msg):
        frame = self.frame_message(8,seqnum,ip,port,self.ip+ ':' + str(self.port))
        return frame

    def create_key_flood(self,seqnum,ip,port,msg):
        frame = self.frame_message(7,seqnum,ip,port,msg=msg)
        return frame

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 3:
        print('Wrong number of args')
        sys.exit(0)
    else:
        port = int(sys.argv[1])
        file = sys.argv[2]
        list_con = ' '.join(sys.argv[3:])
        #TODO implement parsing of ip:ports
        print(list_con)
        servent = Servent(port,file,list_con)
        print(servent.keyval)
        servent.run()
