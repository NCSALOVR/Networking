import socket
import threading
import os
import json
import sys
import time
import jsonManager as jm
import profile as pro

central_json_data = {}
profiles = []

def threadFunc(conn):
    global central_json_data
    global profiles
    #check with registration
    conn.send("Registered?")
    id = conn.recv(1024)
    p  = 0
    if id == "new":
        p = pro.Profile(id,central_json_data,profiles)
        profiles.append(p)
        conn.send(str(p.id))
    else: 
        t = long(id)
        for x in profiles:
            if x.id == t:
                p = x
        #TODO: when id is not a number and when id is not an id of the existing profile
        
    #receiving data to be used in update/delete from client
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
        for x in profiles:
            x.update = jm.update(x.update,local_json_data)
    elif action == 'delete':
        central_json_data = jm.delete(central_json_data, local_json_data)
        for x in profiles:
            x.delete = jm.update(x.delete,local_json_data)

    #send the updated one back to client
    if action == 'update':
        conn.send(str(len(json.dumps(p.update))))
        time.sleep(.0001)
        conn.send(json.dumps(p.update))
        p.update = {}
    elif action == 'delete':
        conn.send(str(len(json.dumps(p.delete))))
        time.sleep(.0001)
        conn.send(json.dumps(p.delete))
        p.delete = {}
    else:
        conn.send(str(len(json.dumps(central_json_data))))
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

    
