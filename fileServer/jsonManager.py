import os
import json
import sys
import time

'''
The function to update (i.e., add/change) centralJson data with localJson.
The retrn value is the modified centralJson.
'''
def update(centralJson, localJson):
    if centralJson == {}:
        centralJson = localJson
    elif type(centralJson) is dict and type(localJson) is dict:
        for local_key, local_value in localJson.iteritems():
            if local_key in centralJson:
                if (type(centralJson[local_key] ) is dict) or (type(centralJson[local_key] ) is list):
                    centralJson[local_key] = update(centralJson[local_key], localJson[local_key])
                else:
                    centralJson[local_key] = localJson[local_key]
            else:
                centralJson[local_key] = localJson[local_key]
    #To update the list, the old list is simply replaced by the new list. 
    #This is suited with the current way that VIVE send the update data; it might need to be edited in the future.
    elif type(centralJson) is list and type(localJson) is list:
        centralJson = localJson
	'''
        for local_elem in localJson:
            if local_elem not in centralJson:
                centralJson.append(local_elem)   
	'''
    return centralJson

'''
The function to delete localJson from centralJson data.
The return value is the modified centralJson.
'''
def delete(centralJson, localJson):
    if type(centralJson) is dict and type(localJson) is dict:
        for local_key, local_value in localJson.iteritems():
            if local_key in centralJson:
                if (type(centralJson[local_key] ) is dict) or (type(centralJson[local_key] ) is list):
                    centralJson[local_key] = delete(centralJson[local_key], localJson[local_key])
                else:
                    if centralJson[local_key] == local_value:
                        del centralJson[local_key]
                        
    elif type(centralJson) is list and type(localJson) is list:
        for local_elem in localJson:
            if local_elem in centralJson:
                centralJson.remove(local_elem)
    
    return centralJson
