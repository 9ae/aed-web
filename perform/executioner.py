'''
Created on Sep 28, 2013

@author: alice
'''

import janus

from threading import Thread
import threading

class Executioner(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.exp = None
		self.stop_flag = False
	
	def run(self,exp):
		self.exp = exp
		self.exp.new_trial()
		while not(self.stop_flag):
			self.exp.loop()
			#just for testing
			if self.exp.trials_count()>3:
				self.stop()
			
		print 'finished'

	def stop(self):
		self.stop_flag = True