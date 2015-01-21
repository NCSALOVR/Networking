# -*- coding: utf-8 -*-
'''
Created on 14 ม.ค. 2558

@author: prinnb
'''
import json
import unittest

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
    
if __name__ == '__main__':
    central_json_file = open('central.json')
    central_data = json.load(central_json_file)
    central_json_file.close()
    
    local_json_file = open('local.json')
    local_data = json.load(local_json_file)
    local_json_file.close()
    central_data = update(central_data, local_data)
    print central_data
    
    
class TestJson(unittest.TestCase):
    def setUp(self):
        self.central_json_file = open('central.json')
        self.central_data = json.load(self.central_json_file)
        self.central_json_file.close()
    def test_add_list(self):
        local_data = json.loads('{"children": ["Tom"]}')
        new_central_data = update(self.central_data, local_data)
        self.assertTrue("Tom" in new_central_data['children'])

    def test_add_dict(self):
        local_data = json.loads('{"college": "UIUC"}')
        new_central_data = update(self.central_data, local_data)
        self.assertTrue("college" in new_central_data)
        
    def test_remove_list(self):
        local_data = json.loads('{"spouse": ["Marry"]}')
        new_central_data = remove(self.central_data, local_data)
        self.assertFalse("Marry" in new_central_data['spouse'])

    def test_remove_dict(self):
        local_data = json.loads('{"firstName": "John"}')
        new_central_data = remove(self.central_data, local_data)
        self.assertFalse("firstName" in new_central_data)
        
    def test_remove_dict_in_list(self):
        local_data = json.loads('{"phoneNumbers": [{"number": "212 555-1234", "type": "home"}]}')
        new_central_data = remove(self.central_data, local_data)
        self.assertEqual(len(new_central_data['phoneNumbers']), 1)
        
    def test_update_dict(self):
        local_data = json.loads('{"isAlive": false}')
        new_central_data = update(self.central_data, local_data)
        self.assertFalse(new_central_data["isAlive"])
    
    def test_update_list(self):
        local_data = json.loads('{"spouse": ["Betty"]}')
        new_central_data = update(self.central_data, local_data)
        self.assertTrue("Betty" in new_central_data['spouse'])
        self.assertEqual(len(new_central_data['spouse']), 3)
        

    
