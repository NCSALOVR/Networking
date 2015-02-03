import socket
import threading
import os
import json


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
    
    local_json_data = json.loads(clientData)
    central_json_file = open('central.json','r+')
    central_json_data = {}
    if long(os.path.getsize('central.json')) > 0:
	central_json_data = json.load(central_json_file)
    central_json_file.close()

    if action == 'update':
        central_json_data = update(central_json_data, local_json_data)
    elif action == 'remove':
        central_json_data = remove(central_json_data, local_json_data)

    with open('central.json','w+') as outfile:
	json.dump(central_json_data,outfile)
    conn.send(str(os.path.getsize('central.json')))
    with open('central.json','rb') as f:
	bytesToSend = f.read(1024)
	conn.send(bytesToSend)
	while True:
	    bytesToSend = f.read(1024)
	    if not bytesToSend:
		break
	    conn.send(bytesToSend)

    print central_json_data  
    
    conn.send('Thank you')
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

    
