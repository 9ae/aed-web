'''
Created on Sep 28, 2013

@author: alice
'''

import janus

from threading import Thread
from decimal import Decimal
import libarian

class Executioner(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.stop_flag = False
		self.intervals = []
		self.interval_pointer = 0
		self.is_new_trial = False
		self.trial_duration = Decimal(0.0)
	
	def set_dictator(self,dictator):
		self.axe = dictator
	
	def set_timekeeper(self,tk):
		self.tk = tk
	
	def run(self):
		self.axe.new_trial()
		while not(self.stop_flag):
			self.loop()
			#just for testing
			if libarian.get_experiment_terminate():
				self.stop_flag = True
		#finished
		self.axe.complete()
		print 'experiment end'
	

	def trials_count(self):
		return len(self.tk.timelog)

	def loop(self):
		# check time       
		trial_time = self.tk.trial_diff()
		current_interval = self.intervals[self.interval_pointer]
	
		if self.is_new_trial:
			current_interval.at_begin()
			self.is_new_trial = False

		if trial_time > current_interval.duration:
			# go to next interval
			current_interval.at_end()
			self.interval_pointer = self.interval_pointer + 1
			if self.interval_pointer >= len(self.intervals):
				# is at last interval
				self.axe.new_trial()
				return
			# start new interval
			next_interval = self.intervals[self.interval_pointer]
			next_interval.at_begin()
			next_interval.meanwhile()
		else:
			current_interval.meanwhile()
