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
        centralJson = centralJson+localJson
        '''
        use this instead if duplication in the list is NOT allowed
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
    totalReceive = len(clientData)

    while totalReceive < clientFileSize:
        clientData  = clientData+conn.recv(1024)
        totalReceive += len(clientData)
    print "File Received"

    print clientData
    local_json_data = json.loads(clientData)
    central_json_file = open('central.json')
    central_json_data = json.load(central_json_file)
    central_json_file.close()

    if action == 'update':
        central_json_data = update(central_json_data, local_json_data)
    elif action == 'remove':
        central_json_data = remove(central_json_data, local_json_data)

    #TODO: save the central.json and send the updated one back to client
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

    