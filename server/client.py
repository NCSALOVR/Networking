import socket
import os
import array
import binascii
import SocketServer
import base64 as b64
from hashlib import sha1

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("127.0.0.1",8888))
toSend = ""
while toSend!="end":
	received = s.recv(2048)
	print "Server: ", received
	toSend = raw_input("Client: ")
	s.sendall(toSend)
