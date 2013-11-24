'''
Created on Nov 23, 2013

@author: alice
'''

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