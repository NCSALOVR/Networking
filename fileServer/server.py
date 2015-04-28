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

'''
The function to be run on a thread and send update/delete data to the clients every t second(s).
'''
def period(conn,id,t):
    global toEnd
    while(True):
        time.sleep(t)
        # toEnd would be set to true when the end command is received in threadFunc()         
        if toEnd:
            break
        stateLock.acquire()
        profileLock.acquire() 
        p = 0
        for x in profiles:
            if x.id == id:
                p = x
        if p.update=={} and p.delete=={}:
            profileLock.release()
            stateLock.release()
            continue
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

'''
The target function to be run on a thread. It receive the command action (and data if applicable) from the client and perform accordingly.
'''
def threadFunc(conn):
    global central_json_data
    global profiles
    global toEnd

    #registration. assign a new id or check that the id receive from the client is valid
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
        #receiving commmand action (i.e., update/delete/period/end/end_register)
        action = sh.recv_msg(conn)
        local_json_data = {}

        #the case to close the first connection to register the id
        if action == 'end_register':
            sh.send_msg(conn, "goodbye")
            print "[Register] Connection with profile "+str(id)+" closed"
            conn.close() 
            return 

        #receive data to be use in update/delete
        if not (action == 'end' or action == 'period'):
            clientData = sh.recv_msg(conn)
            local_json_data = json.loads(clientData)

        #in the case of period action, spawn a thread to periodically send update/delete data to the client.
        if action == 'period':
            t = sh.recv_msg(conn)
            periodThread = threading.Thread(target=period, args=(conn,id,float(t)))
            periodThread.start()

        #in the case of update or delete action, manipulate the central json based on the action and data from client.    
        if action == 'update':
            stateLock.acquire()
            if id in central_json_data:
                central_json_data[id] = jm.update(central_json_data[id], local_json_data)
            else:
                central_json_data[id] = jm.update({},local_json_data)
            for x in profiles:
                profileLock.acquire()
                if id in x.update:
                    x.update[id] = jm.update(x.update[id], local_json_data)
                else:
                    x.update[id] = jm.update({},local_json_data)
                profileLock.release()
            stateLock.release()

        elif action == 'delete':
            stateLock.acquire()
            if id in central_json_data:
                central_json_data[id] = jm.delete(central_json_data[id], local_json_data)
            for x in profiles:
                profileLock.acquire()
                if id in x.update:
                    x.delete[id] = jm.update(x.delete[id], local_json_data)
                else:
                    x.delete[id] = jm.update({},local_json_data)
                profileLock.release()
            stateLock.release()

        #in the case of end action, close the connection.
        elif action == 'end':
            sh.send_msg(conn, "goodbye")
            print "Connection with profile "+str(id)+" closed"
            toEnd = True
            conn.close() 
            return 

    conn.close()


if __name__ == '__main__':
    host = '141.142.21.57'
    port = 8000
    s = socket.socket()
    s.bind((host,port))
    s.listen(3)
    print "Start Server"
    while True:
        conn, addr = s.accept()
        print "Received connection from client: " + str(addr)
        #spawning a thread for each connection with a client
        t = threading.Thread(target=threadFunc, args=(conn,))
        t.start()
    s.close()

    
