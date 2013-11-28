'''
Created on Nov 23, 2013

@author: alice
'''
import json
from django.core.cache import cache

def import_mod_file(filename):
	import os
	import sys
	directory, module_name = os.path.split(filename)
	module_name = os.path.splitext(module_name)[0]
	path = list(sys.path)
	sys.path.append(directory)
	module = None
	try:
		module = __import__(module_name)
	finally:
		sys.path[:] = path # restore
	return module

def poke_cache(key,fun,secs=60):
	val = cache.get(key)
	if val==None:
		val = fun()
		cache.set(key,val,secs)
	return val

class Medea(object):
	def __init__(self):
		self.json = {'errors':[],'content':{}}
		
	def addError(self,msg):
		self.json['errors'].append(msg)
	
	def noErrors(self):
		return len(self.json['errors'])==0
	
	def addContent(self,key,val):
		self.json['content'][key] = val
	
	def serialize(self):
		return json.dumps(self.json)