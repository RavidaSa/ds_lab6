#!/usr/bin/env python3

import sys
import socket
import os
import selectors
from tqdm import tqdm
import types
SEPARATOR = " "
BUFFER_SIZE = 4096 # send 4096 bytes each time step

sel = selectors.DefaultSelector()

filename, host, port = sys.argv[1:4]
filesize = os.path.getsize(filename)

def start_connections(host, port):
    server_addr = (host, port)
    print("starting connection", 1, "to", server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_WRITE
    data = types.SimpleNamespace(
            connid=1,
            msg_total=1,
            recv_total=int,
            messages=filename,
            outb="",
    )
    sel.register(sock, events, data=data)
    

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
     
    if mask & selectors.EVENT_WRITE:
    	if not data.outb and data.messages:
            data.outb = filename.encode()
            
    	with open(filename, "rb") as f:
            progress = tqdm(total=os.path.getsize(filename))
            sock.sendall(data.outb)
            rec = f.read(BUFFER_SIZE)
            while rec:
                sock.send(rec)
                progress.update(len(rec))
                rec = f.read(BUFFER_SIZE)
                
                
            
            


if len(sys.argv) != 4:
    print("usage:", sys.argv[0], "<filename><host> <port>")
    sys.exit(1)



start_connections(host, int(port))

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()

