import socket
import threading
import os
import json
import sys
import time
import jsonManager as jm
import profile as pro
import socketHelper as sh

central_json_data = {}
profiles = []

def threadFunc(conn):
    global central_json_data
    global profiles
    #check with registration
    sh.send_msg(conn,"Registered?")
    id = sh.recv_msg(conn)
    p  = 0
    if id == "new":
        p = pro.Profile(id,central_json_data,profiles)
        profiles.append(p)
        sh.send_msg(conn, str(p.id))
    else: 
        t = long(id)
        for x in profiles:
            if x.id == t:
                p = x
        #TODO: when id is not a number and when id is not an id of the existing profile
    id = p.id    

    #receiving data to be used in update/delete from client
    action = sh.recv_msg(conn)
    clientData = sh.recv_msg(conn)
    print "File Received"

    #manipulate the central json based on the action and data from client    
    local_json_data = json.loads(clientData)
    if action == 'update':
        if id in central_json_data:
            central_json_data[id] = jm.update(central_json_data[id], local_json_data)
        else:
            central_json_data[id] = jm.update({},local_json_data)
        for x in profiles:
            if id in x.update:
                x.update[id] = jm.update(x.update[id],local_json_data)
            else:
                x.update[id] = jm.update({},local_json_data)

    elif action == 'delete':
        if id in central_json_data:
            central_json_data[id] = jm.delete(central_json_data[id], local_json_data)
        for x in profiles:
            if id in x.delete:
                x.delete[id] = jm.update(x.delete[id],local_json_data)
            else:
                x.delete[id] = jm.update({},local_json_data)

    #send the updated one back to client
    if action == 'update':
        sh.send_msg(conn, json.dumps(p.update))
        p.update = {}
    elif action == 'delete':
        sh.send_msg(conn, json.dumps(p.delete))
        p.delete = {}
    else:
        sh.send_msg(conn, json.dumps(central_json_data))
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

    
