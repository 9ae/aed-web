import aedsdk
import time
from decimal import Decimal
import random

class Mickey(aedsdk.Paradigm):
	
	def __init__(self):
		aedsdk.Paradigm.__init__(self)
	
	@staticmethod	
	def varyInterval(interval):
		if interval.varyby!=0:
			varyhalf = float(interval.varyby)*0.5
			interval.duration = interval.oridur + Decimal(random.uniform(-1.0*varyhalf, varyhalf))
	
	class LeverPress(aedsdk.Action):
		def __init__(self):
			pass
		
		def detect(self):
			return self.exe.check_emulate_action('LeverPress')
	
	class Reward(aedsdk.Event):
		def __init__(self):
			self.valve = 0

		def perform(self,time=None):
			self.exe.event_happen('Reward from valve %d'%(self.valve),given_time=time)
		
		def set_prop(self,name,val):
			if name=="valve":
				self.valve = int(val)
		
		def __str__(self):
			return "Reward { valve:"+str(self.valve)+" }"
		
	class Restart(aedsdk.Event):
		def __init__(self):
			pass
		
		def perform(self,time=None):
			#self.exe.event_happen('Restart trial')
			self.exe.new_trial()
	
	class Wait(aedsdk.Interval):   
		def __init__(self,  duration=0.0):
			aedsdk.Interval.__init__(self, duration)
			self.varyby = 0.0
			self.oridur = self.duration
		
		def init_duration(self,value):
			val = Decimal(value)
			self.oridur = val
			self.duration = val
			
		def on_LeverPress(self):
			for act in self.events_LeverPress:
				act.perform()
		
		def at_begin(self):
			Mickey.varyInterval(self)
			aedsdk.Interval.at_begin(self)
			self.exe.interval_happen('Begin Wait')
			
		def at_end(self):
			aedsdk.Interval.at_end(self)
		
		def meanwhile(self):
			if self.a_LeverPress.detect():
				self.on_LeverPress()
		
		def set_prop(self,name,val):
			if name=="varyby":
				self.varyby = Decimal(val)
			
	class Tone(aedsdk.Interval):
		def __init__(self, duration=0.0):
			aedsdk.Interval.__init__(self, duration)
			self.varyby = 0.0
			self.oridur = self.duration
		
		def init_duration(self,value):
			val = Decimal(value)
			self.oridur = val
			self.duration = val
		
		def at_begin(self):
			Mickey.varyInterval(self)
			aedsdk.Interval.at_begin(self)
			self.exe.interval_happen('Begin Tone')
		
		def at_end(self):
			aedsdk.Interval.at_end(self)
			
		def meanwhile(self): pass
		
		def set_prop(self,name,val):
			if name=="varyby":
				self.varyby = Decimal(val)	
	
	class Present(aedsdk.Interval):
		def __init__(self, duration=0.0):
			aedsdk.Interval.__init__(self, duration)
			self.varyby = 0.0
			self.oridur = self.duration
		
		def init_duration(self,value):
			val = Decimal(value)
			self.oridur = val
			self.duration = val
		
		def at_begin(self):
			Mickey.varyInterval(self)
			aedsdk.Interval.at_begin(self)
			self.exe.interval_happen('Begin Present')
		
		def at_end(self):
			aedsdk.Interval.at_end(self)		
		
		def on_LeverPress(self):
			#self.exe.action_happen('Lever Pressed on Present interval')
			for act in self.events_LeverPress:
				act.perform()
				
		def meanwhile(self):
			if self.a_LeverPress.detect():
				self.on_LeverPress()
		
		def set_prop(self,name,val):
			if name=="varyby":
				self.varyby = Decimal(val)
	
	class Refrain(aedsdk.Interval):
		def __init__(self, duration=0.0):
			aedsdk.Interval.__init__(self, duration)
			self.reward = True
			self.varyby = 0.0
			self.oridur = self.duration
		
		def init_duration(self,value):
			val = Decimal(value)
			self.oridur = val
			self.duration = val
		
		def at_begin(self):
			Mickey.varyInterval(self)
			aedsdk.Interval.at_begin(self)
			self.exe.interval_happen('Begin Refrain')
		
		def at_end(self):
			if self.reward:
				aedsdk.Interval.at_end(self)
				self.exe.event_happen('Reward from valve %d at the end of a Refrain interval'%(self.valve))
			else:
				pass
		
		def on_LeverPress(self):
			self.reward = False
			#self.exe.action_happen('Lever Pressed on Refrain interval')
			for act in self.events_LeverPress:
				act.perform()
				
		def meanwhile(self):
			if self.a_LeverPress.detect():
				self.on_LeverPress()
				
		def set_prop(self,name,val):
			if name=="varyby":
				self.varyby = Decimal(val)	