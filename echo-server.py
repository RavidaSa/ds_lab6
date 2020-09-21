#!/usr/bin/env python3

import sys
import socket
import selectors
import os
from tqdm import tqdm
import types

BUFFER_SIZE = 4096
SEPARATOR = ":"

sel = selectors.DefaultSelector()


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(0)
    data = types.SimpleNamespace(addr=addr,  inb=b"", outb=b"", filename ="", size=int )
    events = selectors.EVENT_READ 
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:

    	if data.filename == "":
		    rec_filename = sock.recv(BUFFER_SIZE).decode()
		    filename = rec_filename
		    
		    print(filename)
		    filename = os.path.basename(filename)
		    tempname = filename
		    copy = 0
		    print(tempname)
		    while os.path.isfile(tempname):
			    copy += 1
			    base = filename.split('.')[0]
			    type = filename.split('.')[1]
			    tempname = base + '_copy' + str(copy) + '.' + type
		    data.filename = tempname
		    print(data.filename)

    	with open(data.filename, "wb") as f:
		    print(data.filename)
		    
		    while True:
        		bytes_read = sock.recv(BUFFER_SIZE)
        		if bytes_read:
        			f.write(bytes_read)
        		else:
        			print("closing connection to", data.addr)
        			sel.unregister(sock)
        			sock.close()
        			break


if len(sys.argv) != 3:
    print("usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
