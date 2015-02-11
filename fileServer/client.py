import socket
import os
import threading
import json

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8000

    s = socket.socket()
    s.connect((host, port))
    mesg = s.recv(1048)
    action = raw_input(mesg)
    id = 0
    if action == "new":
	   s.send(action)
	   id = long(s.recv(1024))
	   print id
    else:
	   s.send(action)
    #sending data to be used in update/delete to server
    action = raw_input("Action(update/delete)? -> ")
    s.send(action)
    filePath = raw_input("Json file path to use for update/delete? -> ")
    s.send(str(os.path.getsize(filePath)))

    with open(filePath, 'rb') as f:
        bytesToSend = f.read(1024)
        s.send(bytesToSend)
        while True:
            bytesToSend = f.read(1024)
            if not bytesToSend:
                break
            s.send(bytesToSend)
    f.close()

    #receiving and saving updated json from server
    serverDataSize = long(s.recv(1024))
    
    serverData = s.recv(serverDataSize)
    print serverData
    s.close()

    
