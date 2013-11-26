'''
Created on Sep 28, 2013

@author: alice
'''

import janus

from threading import Thread
from models import Experiment

class Executioner(Thread):
	def __init__(self,nickname=''):
		Thread.__init__(self)
		self.stop_flag = False
		self.intervals = []
		self.events = []    
		self.tk = janus.Timekeeper(-3)
		self.interval_pointer = 0
		self.is_new_trial = False
		self.exp = Experiment(name=nickname)
	
	def run(self, exp):
		self.exp.save()
		self.new_trial()
		while not(self.stop_flag):
			self.loop()
			#just for testing
			if self.exp.trials_count() > 3:
				self.stop()
		#finished

	def stop(self):
		self.stop_flag = True
		
	def new_trial(self):
		self.interval_pointer = 0
		self.tk.new_trial()
		self.is_new_trial = True

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
				self.new_trial()
				return
			# start new interval
			next_interval = self.intervals[self.interval_pointer]
			next_interval.at_begin()
			next_interval.meanwhile()
		else:
			current_interval.meanwhile()
