import socket
import os
import threading
import json
import socketHelper as sh
import time
id = 0
updates = []
deletes = []
commands = []
dataLock = threading.Lock()
updateLock = threading.Lock()

def threadCtoS():
    host = '127.0.0.1'
    c_to_s_port = 8000
    c_to_s_soc = socket.socket()
    c_to_s_soc.connect((host,c_to_s_port))
    if not (handshake(c_to_s_soc)):
        updateLock.release()
        return 
    while(True):
        command = getCommand()
        if(len(command)==0):
            continue
        action = command[0]
        if not (action=="end" or action=="update" or action == "delete"):
            continue
        sh.send_msg(c_to_s_soc,action)
        if(len(command)==2):
            data = command[1]
            sh.send_msg(c_to_s_soc,json.dumps(data))
        #receiving the update from server
        serverData = sh.recv_msg(c_to_s_soc)
        if serverData == "goodbye":
            c_to_s_soc.close()
            updateLock.release()
            break

def getUpdate():
    dataLock.acquire()
    if len(updates)==0:
        dataLock.release()
        return {}
    temp = updates.pop(0)
    dataLock.release()
    return temp

def getDelete():
    dataLock.acquire()
    if len(deletes)==0:
        dataLock.release()
        return {}
    temp = deletes.pop(0)
    dataLock.release()
    return temp

def getCommand():
    dataLock.acquire()
    if len(commands)==0:
        dataLock.release()
        return []
    temp = commands.pop(0)
    dataLock.release()
    return temp

def sendCommand(command, data = {}):
    if len(data.keys())==0:
        dataLock.acquire()
        commands.append([command])
        dataLock.release()
        return
    dataLock.acquire()
    commands.append([command,data])
    dataLock.release()
    return

def period(conn,t):
    try:
        update = sh.recv_msg(conn)
        delete = sh.recv_msg(conn)
    except:
        return
    dataLock.acquire()
    if len(update)>0:
        updates.append(json.loads(update))
    if len(delete)>0:
        deletes.append(json.loads(delete))
    dataLock.release()
    threading.Timer(t,period,[conn,t]).start()

def threadStoC(t):
    host = '127.0.0.1'
    s_to_c_port = 8000
    s_to_c_soc = socket.socket()
    s_to_c_soc.connect((host,s_to_c_port))
    if handshake(s_to_c_soc):
        sh.send_msg(s_to_c_soc,"period")
        sh.send_msg(s_to_c_soc,str(t))
        timer = threading.Timer(t,period,[s_to_c_soc,t])
        timer.start()
        updateLock.acquire()
        updateLock.release()
        timer.cancel()
        sh.send_msg(s_to_c_soc,"end")
        s_to_c_soc.close()
    print "threadStoC finished"

def handshake(s):
    try: 
        sh.send_msg(s, str(id))
        error_code = sh.recv_msg(s)
        if not error_code == "ok":
            print error_code
            s.close()
            return False
        return True
    except:
        return False

def begin(reg,t):
    host = '127.0.0.1'
    port = 8000

    action = reg
    if action == "end":
        print "Goodbye"
        quit()
    s = socket.socket()
    s.connect((host,port))
    if action == "new":
        sh.send_msg(s, action)
        id = long(sh.recv_msg(s))
    else:
        sh.send_msg(s, action)
    error_code = sh.recv_msg(s)
    if not error_code == "ok":
        print error_code
        s.close()
        print "Please exit the program now"
        return

    if action != "new":
        id = long(action)
        
    print "You are id "+str(id)
    print "Use that id to login in the future"
    sh.send_msg(s,"end")
    sh.recv_msg(s)
    s.close()
    updateLock.acquire()
    t_write = threading.Thread(target=threadCtoS, args=())
    t_read = threading.Thread(target=threadStoC, args=(t,))
    t_write.start()
    t_read.start()
