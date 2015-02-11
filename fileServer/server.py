import socket
import threading
import os
import json
import sys
import time
import jsonManager as jm

central_json_data = {}



def threadFunc(conn):
    global central_json_data
    #receiving data to be used in update/remove from client
    action = conn.recv(1024)
    clientFileSize = long(conn.recv(1024))
    print clientFileSize
    clientData = conn.recv(1024)
    totalRecv = len(clientData)
    while totalRecv < clientFileSize:
        receive = conn.recv(1024)
        totalRecv += len(receive)
        clientData = clientData+receive
    print "File Received"
    #manipulate the central json based on the action and data from client    
    local_json_data = json.loads(clientData)
    if action == 'update':
        central_json_data = jm.update(central_json_data, local_json_data)
    elif action == 'remove':
        central_json_data = jm.remove(central_json_data, local_json_data)


    #send the updated one back to client
    conn.send(str(sys.getsizeof(json.dumps(central_json_data))))
    time.sleep(.0001)
    conn.send(json.dumps(central_json_data))

    print central_json_data  
    conn.close()


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8000
    s = socket.socket()
    s.bind((host,port))
    s.listen(1)
    print "Start Server"
    while True:
        conn, addr = s.accept()
        print "Received connection from client: " + str(addr)
        t = threading.Thread(target=threadFunc, args=(conn,))
        t.start()
    s.close()

    
