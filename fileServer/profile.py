import os
import json
import sys
import time
import copy

class Profile:
	def __init__(self, name, id, update):
		self.name = name
		self.id = id
		self.update = copy.deepcopy(update)
		self.delete = {}
	def __init__(self,name,update,list):
		self.name = name
		t = 0
		for p in list:
			t = max(p.id + 1,t)
		self.id = t
		self.update = copy.deepcopy(update)
		self.delete = {}
