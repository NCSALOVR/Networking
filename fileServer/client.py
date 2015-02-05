import socket
import os
import threading
import json

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8000

    s = socket.socket()
    s.connect((host, port))

    #sending data to be used in update/remove to server
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
    f.close()

    #receiving and saving updated json from server
    serverDataSize = long(s.recv(1024))
    
    updatedFilePath = raw_input("Path to save updated json? -> ")
    f = open(updatedFilePath, 'wb')
    serverData = s.recv(serverDataSize)
    f.write(serverData)
    print "Updated File Saved"
    f.close()
    s.close()

    
