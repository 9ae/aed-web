import aedsdk
import time

import random

class Mickey(aedsdk.Paradigm):
	
	def __init__(self):
		aedsdk.Paradigm.__init__(self)

	class LeverPress(aedsdk.Action):
		def __init__(self):
			pass
		
		def detect(self):
			if random.randint(1,1e4)==3:
				return True
			else:
				return False
	
	class Reward(aedsdk.Event):
		def __init__(self):
			self.valve = 0

		def perform(self):
			print 'reward delivered @ %f'%self.exp.tk.diff()
		
		def set_prop(self,name,val):
			if name=="valve":
				self.valve = int(val)
		
		def __str__(self):
			return "Reward { valve:"+str(self.valve)+" }"
		
	class Restart(aedsdk.Event):
		def __init__(self):
			pass
		
		def perform(self):
			self.exp.new_trial()
			print 'restart trial @ %f'%self.exp.tk.diff()
	
	class Wait(aedsdk.Interval):   
		def __init__(self,  duration=0.0):
			aedsdk.Interval.__init__(self, duration)
			
		def on_LeverPress(self):
			print 'lever pressed'
			for act in self.events_LeverPress:
				act.perform()
		
		def at_begin(self):
			aedsdk.Interval.at_begin(self)
			print 'wait start @ %f'%self.exp.tk.diff()
			
		def at_end(self):
			aedsdk.Interval.at_end(self)
			print 'wait end @ %f'%self.exp.tk.diff()
		
		def meanwhile(self):
			if self.a_LeverPress.detect():
				self.on_LeverPress()
			
	class Tone(aedsdk.Interval):
		def __init__(self, duration=0.0):
			aedsdk.Interval.__init__(self, duration)
		
		def at_begin(self):
			aedsdk.Interval.at_begin(self)
			print 'tone play start @ %f'%self.exp.tk.diff()
		
		def at_end(self):
			aedsdk.Interval.at_end(self)
			print 'tone play end @ %f'%self.exp.tk.diff()
			
		def meanwhile(self): pass
	
	class Present(aedsdk.Interval):
		def __init__(self, duration=0.0):
			aedsdk.Interval.__init__(self, duration)
		
		def at_begin(self):
			aedsdk.Interval.at_begin(self)
			print 'reward chance start @ %f'%self.exp.tk.diff()
		
		def at_end(self):
			aedsdk.Interval.at_end(self)
			print 'reward chance end @ %f'%self.exp.tk.diff()
		
		
		def on_LeverPress(self):
			print 'give reward :) @ %f'%self.exp.tk.diff()
			for act in self.events_LeverPress:
				act.perform()
				
		def meanwhile(self):
			if self.a_LeverPress.detect():
				self.on_LeverPress()
	
	class Refrain(aedsdk.Interval):
		def __init__(self, duration=0.0):
			aedsdk.Interval.__init__(self, duration)
			self.reward = True
		
		def at_end(self):
			if self.reward:
				aedsdk.Interval.at_end(self)
				print 'reward given  @ %f'%self.exp.tk.diff()
			else:
				print 'reward not given  @ %f'%self.exp.tk.diff()
		
		def on_LeverPress(self):
			self.reward = False
			print 'oops pressed lever no reward at the end :(  @ %f'%self.exp.tk.diff()
			for act in self.events_LeverPress:
				act.perform()
				
		def meanwhile(self):
			if self.a_LeverPress.detect():
				self.on_LeverPress()