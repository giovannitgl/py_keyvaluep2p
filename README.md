# py_keyvaluep2p
P2P Key value storage, developed for Python 3.5 +

        Protocol is defined as:
        
        KeyReq (type = 5)
        | Type | SeqNum |        Key        |
        0         2     6              6 + length*2
        
        TopoReq (type = 6)
        | Type | SeqNum |
        0      2        6
        
        (Key/Topo)Flood (type = 7 or 8)
        | Type | TTL | SeqNum | Orig_IP | Orig_Port |      Info        |
        0     2      4        8        12          14               14+length*2
        
        Answr
        | Type | SeqNum |       Key        |
        0         2     6            6 + length*2

        Numbers are bytes, max length = 400.
        
  ## How to run:
  python client.py ip:port
  python servent.py port dictfile ip1:port1 ip2:port2 ... ipn:portn 
  
  ## Commands:
  In client you can run three types of commands:
*       ? <key>
        Query the value for the given key
*       T
        Asks the network topology
*       Q
        Quit
