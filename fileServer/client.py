import socket
import os
import threading
import json

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8000

    s = socket.socket()
    s.connect((host, port))

    action = raw_input("Action(update/remove)? -> ")
    s.send(action)
    filePath = raw_input("Json file path to use for update/remove? -> ")
    s.send(str(os.path.getsize(filePath)))

    with open(filePath, 'rb') as f:
        bytesToSend = f.read(1024)
        s.send(bytesToSend)
        while True:
            bytesToSend = f.read(1024)
            if not bytesToSend:
                break
            s.send(bytesToSend)
            print bytesToSend

    fileSize = long(s.recv(1024))
    result = str(s.recv(1024))
    received = len(result)
    while received < fileSize:
	result = result + str(s.recv(1024))
    print result
    print str(s.recv(1024))
    s.close()

    
