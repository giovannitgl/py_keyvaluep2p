# py_keyvaluep2p
P2P Key value storage

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