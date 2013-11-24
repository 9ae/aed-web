'''
Created on Aug 29, 2013

@author: alice
'''
from datetime import datetime

def last(L):
	lenny = len(L)
	if lenny==0:
		return None
	else:
		return L[lenny-1]
	
""" initalized at the start of an experiment """
class Timekeeper(object):
	def __init__(self,unit):
		self.unit = unit
		self.startTime = datetime.now()
		self.timelog = []

	def millisec(self,t):
		s = str(t.days * 24 * 60 * 60 + t.seconds)
		mus = str(t.microseconds)
		mus = mus.rjust(6,'0')
		mis = mus[0:3]
		return float(s+'.'+mis)
	
	def diff(self):
		time_diff = datetime.now() - self.startTime
		return self.millisec(time_diff)
	
	def trial_diff(self):
		trial_start = last(self.timelog)
		if trial_start==None:
			return 0.0
		else:
			time_diff = datetime.now() - trial_start
			return self.millisec(time_diff)
	
	def new_trial(self):
		self.timelog.append(datetime.now())
	
	'''
	def diffSince(self, since, record=None):
		time_diff = datetime.now() - since
		if(record!=None):
			if isinstance(record, str):
				self.timelog[record] = time_diff
			else:
				print 'record must be a string'
		return self.millisec(time_diff)

	def diff(self, record=None):
		return self.diffSince(self.startTime, record=record)
	'''
	
	def get(self,recordName):
		return self.timelog[recordName]
		