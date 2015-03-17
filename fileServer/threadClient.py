import socket
import os
import threading
import json
import socketHelper as sh
import time

def threadCtoS():
    host = '127.0.0.1'
    c_to_s_port = 8000
    c_to_s_soc = socket.socket()
    c_to_s_soc.connect((host,c_to_s_port))
    while(True):
        action = raw_input("Action(update/delete/end)? -> ")
        sh.send_msg(c_to_s_soc,action)
        if action!="end":
             filePath = raw_input("Json file path to use for update/delete? -> ")

             with open(filePath, 'rb') as f:
                 sh.send_msg(c_to_s_soc, f.read())
             f.close()

        #receiving the update from server
        serverData = sh.recv_msg(c_to_s_soc)
        print serverData
        if serverData == "goodbye":
            c_to_s_soc.close()
            break

def threadStoC():
    host = '127.0.0.1'
    s_to_c_port = 9008
    s_to_c_soc = socket.socket()
    s_to_c_soc.connect((host,s_to_c_port))
    time.sleep(3)
    print "threadStoC finished"
    s_to_c_soc.close()


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 9000

    #while(True):
    action = raw_input("Registration ('new'/your id/'end'): ")
    id = 0
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
        #continue

    if action != "new":
        id = long(action)
        
    print "You are id "+str(id)
    print "Use that id to login in the future"
    s.close()

    t_write = threading.Thread(target=threadCtoS, args=())
    t_read = threading.Thread(target=threadStoC, args=())
    t_write.start()
    t_read.start()

    
