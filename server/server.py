import socket
import os
import array
import binascii
import SocketServer

class HandleCheckin(SocketServer.BaseRequestHandler):
    def handle(self):
        req = self.request
	test = ""
	while test != "end":
        	req.sendall(raw_input("Server: "))
        	test = req.recv(2048)
		print "Client: ", test

class ThreadedServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = "", int(8888)
    server = ThreadedServer((HOST, PORT), HandleCheckin)
    server.allow_reuse_address = True
    server.serve_forever()
