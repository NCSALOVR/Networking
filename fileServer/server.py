import socket
import threading
import os
import json
import sys
import time

central_json_data = {}

def update(centralJson, localJson):
    if type(centralJson) is dict and type(localJson) is dict:
        for local_key, local_value in localJson.iteritems():
            if local_key in centralJson:
                if (type(centralJson[local_key] ) is dict) or (type(centralJson[local_key] ) is list):
                    centralJson[local_key] = update(centralJson[local_key], localJson[local_key])
                else:
                    centralJson[local_key] = localJson[local_key]
            else:
                centralJson[local_key] = localJson[local_key]
            
    elif type(centralJson) is list and type(localJson) is list:
        centralJson = localJson
	'''
        for local_elem in localJson:
            if local_elem not in centralJson:
                centralJson.append(local_elem)   
	'''
    return centralJson


def remove(centralJson, localJson):
    if type(centralJson) is dict and type(localJson) is dict:
        for local_key, local_value in localJson.iteritems():
            if local_key in centralJson:
                if (type(centralJson[local_key] ) is dict) or (type(centralJson[local_key] ) is list):
                    centralJson[local_key] = remove(centralJson[local_key], localJson[local_key])
                else:
                    if centralJson[local_key] == local_value:
                        del centralJson[local_key]
                        
    elif type(centralJson) is list and type(localJson) is list:
        for local_elem in localJson:
            if local_elem in centralJson:
                centralJson.remove(local_elem)
    
    return centralJson


def threadFunc(conn):
    #receiving data to be used in update/remove from client
    action = conn.recv(1024)
    clientFileSize = long(conn.recv(1024))
    print clientFileSize
    clientData = conn.recv(1024)
    totalRecv = len(clientData)
    while totalRecv < clientFileSize:
        receive = conn.recv(1024)
        totalRecv += len(receive)
        clientData = clientData+receive
    print "File Received"

    #manipulate the central json based on the action and data from client    
    local_json_data = json.loads(clientData)
    global central_json_data
    central_json_data = {}

    try:
        with open('central.json','r+') as central_json_file:
            if long(os.path.getsize('central.json')) > 0:
                central_json_data = json.load(central_json_file)
    except IOError as e:
        print "Unable to open central.json"

    if action == 'update':
        central_json_data = update(central_json_data, local_json_data)
    elif action == 'remove':
        central_json_data = remove(central_json_data, local_json_data)

    #save the updated central json (save to different location for testing).
    with open('central_updated.json','w+') as outfile:
	   json.dump(central_json_data,outfile)

    #send the updated one back to client
    conn.send(str(sys.getsizeof(json.dumps(central_json_data))))
    time.sleep(.0001)
    conn.send(json.dumps(central_json_data))

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

    
