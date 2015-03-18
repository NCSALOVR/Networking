import socket
import os
import threading
import json
import socketHelper as sh
import threadClient

if __name__ == '__main__':

    action = raw_input("Registration ('new'/your id/'end'): ")
    t = 1
    try:
        interval = raw_input("Interval between updates(seconds): ")
        t = float(interval)
    except:
        pass
    threadClient.begin(action,t)
    while(True):
        action = raw_input("Action(update/delete/end)? -> ")
        data = {}
        if action=="update" or action=="delete":
            filePath = raw_input("Json file path to use for update/delete? -> ")
            try:
                f = open(filePath)
                data = json.load(f)
                f.close()
            except:
                print("Not a valid file: "+filePath)
                continue
        threadClient.sendCommand(action,data)
        if(action=="end"):
            break
