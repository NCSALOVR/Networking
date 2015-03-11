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
    id = sh.recv_msg(conn)
    p  = 0
    if id == "new":
        p = pro.Profile(id,central_json_data,profiles)
        profiles.append(p)
        sh.send_msg(conn, str(p.id))
    else:
        if not id.isdigit():
            sh.send_msg(conn, "Error! "+id+" is NaN!")
            print "Error! "+id+" is NaN!"
            conn.close()
            return
        t = long(id)
        found = False
        for x in profiles:
            if x.id == t:
                p = x
                found = True
        if not found:
            sh.send_msg(conn, "Error! Profile "+str(t)+" not found!")
            print "Error! Profile "+str(t)+" not found! Closing connection..."
            conn.close()
            return
    sh.send_msg(conn,"ok")
    id = p.id    
    while(True):
        #receiving data to be used in update/delete from client
        action = sh.recv_msg(conn)
        if action != 'end':
            clientData = sh.recv_msg(conn)
            local_json_data = json.loads(clientData)
            print "File Received"

        #manipulate the central json based on the action and data from client    
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
        elif action == 'end':
            sh.send_msg(conn, "goodbye")
            print "Connection with profile "+str(id)+" closed"
            conn.close() 
            return 

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

    
