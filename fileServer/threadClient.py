'''
The prototype version. Please refer to ../WinCPPClient/WinCPPClient/threadClient.cpp for the actual c++ code that is used in VIVE.
Note: There might be small differences due to different in the two languages.
'''
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
    host = '141.142.21.57'
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

        if action == "end":    
            serverData = sh.recv_msg(c_to_s_soc)
            if serverData == "goodbye":
                c_to_s_soc.close()
                updateLock.release()
                break
    print "threadCtoS finished"

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

def threadStoC(t):
    host = '141.142.21.57'
    s_to_c_port = 8000
    s_to_c_soc = socket.socket()
    s_to_c_soc.connect((host,s_to_c_port))
    s_to_c_soc.settimeout(t)

    if not (handshake(s_to_c_soc)):
        print "handshake s_to_c error"
        return

    sh.send_msg(s_to_c_soc,"period")
    sh.send_msg(s_to_c_soc,str(t))
    while(True):
        time.sleep(t)
        if(updateLock.acquire(False)):
            updateLock.release()
            sh.send_msg(s_to_c_soc,"end")
            sh.recv_msg(s_to_c_soc)
            s_to_c_soc.close()
            break;
        try:
            update = sh.recv_msg(s_to_c_soc)
            delete = sh.recv_msg(s_to_c_soc)
        except:
            continue
        dataLock.acquire()
        if update != "{}":
            updates.append(json.loads(update))
        if delete != "{}":
            deletes.append(json.loads(delete))
        dataLock.release()
    print "threadStoC finished"

def handshake(s):
    try: 
        sh.send_msg(s, str(id))
        error_code = sh.recv_msg(s)
        if not error_code == "ok":
            print error_code
            s.close()
            print "Error, please close program"
            return False
        return True
    except:
        print "Error in handshake, please close program"
        return False

def begin(reg,t):
    global id
    host = '141.142.21.57'
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
    sh.send_msg(s, "end_register")
    sh.recv_msg(s)
    s.close()
    updateLock.acquire()
    t_write = threading.Thread(target=threadCtoS, args=())
    t_read = threading.Thread(target=threadStoC, args=(t,))
    t_write.start()
    t_read.start()
