import socket
import os
import threading
import json
import socketHelper as sh

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8000

    s = socket.socket()
    s.connect((host, port))
    mesg = sh.recv_msg(s)
    action = raw_input(mesg)
    id = 0
    if action == "new":
        sh.send_msg(s, action)
        id = long(sh.recv_msg(s))
        print id
    else:
        sh.send_msg(s, action)

    #sending data to be used in update/delete to server
    action = raw_input("Action(update/delete)? -> ")
    sh.send_msg(s,action)
    filePath = raw_input("Json file path to use for update/delete? -> ")

    with open(filePath, 'rb') as f:
        sh.send_msg(s, f.read())
    f.close()

    #receiving the update from server

    serverData = sh.recv_msg(s)
    print serverData
    s.close()

    
