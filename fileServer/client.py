import socket
import os
import threading
import json
import socketHelper as sh

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8000

    while(True):
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
            continue

        if action != "new":
            id = long(action)
            
        print "You are id "+str(id)
        print "Use that id to login in the future"

        #sending data to be used in update/delete to server
        while (True):
            action = raw_input("Action(update/delete/end)? -> ")
            sh.send_msg(s,action)
            if action!="end":
                 filePath = raw_input("Json file path to use for update/delete? -> ")

                 with open(filePath, 'rb') as f:
                     sh.send_msg(s, f.read())
                 f.close()

             #receiving the update from server

            serverData = sh.recv_msg(s)
            print serverData
            if serverData == "goodbye":
                s.close()
                break

    
