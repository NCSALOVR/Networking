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
stateLock = threading.Lock()
profileLock = threading.Lock()
toEnd = False

def period(conn,id,t):
    while(True):
        time.sleep(t)        
        if toEnd:
            break;
        stateLock.acquire()
        profileLock.acquire() 
        p = 0
        for x in profiles:
            if x.id == id:
                p = x
        if p.update=={} and p.delete=={}:
            profileLock.release()
            stateLock.release()
            continue;
        try: 
            sh.send_msg(conn, json.dumps(p.update))
            sh.send_msg(conn, json.dumps(p.delete))
            p.update = {}
            p.delete = {}
        except:
            profileLock.release()
            stateLock.release()
            return
        profileLock.release()
        stateLock.release()

def threadFunc(conn):
    global central_json_data
    global profiles
    #check with registration
    id = sh.recv_msg(conn)
    p  = 0
    if id == "new":
        p = pro.Profile(id,central_json_data,profiles)
        profileLock.acquire()
        profiles.append(p)
        profileLock.release()
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
        if not (action == 'end' or action == 'period'):
            clientData = sh.recv_msg(conn)
            local_json_data = json.loads(clientData)
            print "File Received"

        if action == 'period':
            t = sh.recv_msg(conn)
            periodThread = threading.Thread(target=period, args=(conn,id,float(t)))
            periodThread.start()

        #manipulate the central json based on the action and data from client    
        if action == 'update':
            stateLock.acquire()
            if id in central_json_data:
                central_json_data = jm.update(central_json_data, local_json_data)
            else:
                central_json_data = jm.update({},local_json_data)
            for x in profiles:
                profileLock.acquire()
                if id in x.update:
                    x.update = jm.update(x.update,local_json_data)
                else:
                    x.update = jm.update({},local_json_data)
                profileLock.release()
            stateLock.release()

        elif action == 'delete':
            stateLock.acquire()
            if id in central_json_data:
                central_json_data = jm.delete(central_json_data, local_json_data)
            for x in profiles:
                profileLock.acquire()
                if id in x.delete:
                    x.delete = jm.update(x.delete,local_json_data)
                else:
                    x.delete = jm.update({},local_json_data)
                profileLock.release()
            stateLock.release()
        elif action == 'end':
            sh.send_msg(conn, "goodbye")
            print "Connection with profile "+str(id)+" closed"
            toEnd = True
            conn.close() 
            return 

        #send the updated one back to client
        if action == 'update':
            stateLock.acquire()
            profileLock.acquire()
            sh.send_msg(conn, json.dumps(p.update))
            profileLock.release()
            stateLock.release()
        elif action == 'delete':
            stateLock.acquire()
            profileLock.acquire()
            sh.send_msg(conn, json.dumps(p.delete))
            profileLock.release()
            stateLock.release()
        else:
            stateLock.acquire()
            sh.send_msg(conn, json.dumps(central_json_data))
            stateLock.release()
    conn.close()


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8000
    s = socket.socket()
    s.bind((host,port))
    s.listen(3)
    print "Start Server"
    while True:
        conn, addr = s.accept()
        print "Received connection from client: " + str(addr)
        t = threading.Thread(target=threadFunc, args=(conn,))
        t.start()
    s.close()

    
