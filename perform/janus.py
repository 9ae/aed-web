'''
Created on Aug 29, 2013

@author: alice
'''
from datetime import datetime
from decimal import *

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
		getcontext().prec = 8
		s = Decimal(t.days * 24 * 60 * 60 + t.seconds)
		mis = Decimal(t.microseconds)*Decimal(1E-6)
		mis = Decimal(format(mis,'.3f'))
		return s+mis
	
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
	
	def get(self,recordName):
		return self.timelog[recordName]
		