import os
import json
import sys
import time
import copy

'''
The data structure to store each client user along with their update/delete data
'''
class Profile:
    '''
    initialize a profile object with specified id.
    '''
    def __init__(self, name, id, update):
        self.name = name
        self.id = id
        self.update = copy.deepcopy(update)
        self.delete = {}

    '''
    initialize a profile object with the newly assigned id.
    '''
    def __init__(self,name,update,profile_list):
        self.name = name
        t = 0
        for p in profile_list:
            t = max(p.id + 1,t)
        self.id = t
        self.update = copy.deepcopy(update)
        self.delete = {}
        
