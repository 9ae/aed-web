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
		
		@classmethod
		def json(cls):
			result = super(Mickey.LeverPress,cls).json()
			result['color'] = '0000ff'
			return result
		
	
	class Reward(aedsdk.Event):
		def __init__(self):
			self.valve = 0

		def perform(self,time=None):
			self.exe.event_happen('Reward from valve %d'%(self.valve),self.name,given_time=time)
		
		def set_prop(self,name,val):
			if name=="valve":
				self.valve = int(val)
		
		def __str__(self):
			return "Reward { valve:"+str(self.valve)+" }"
		
		@classmethod
		def json(cls):
			result = super(Mickey.Reward,cls).json()
			result['props'].append({'name':'valve','type':'INT'})
			result['color'] = 'ff0000'
			return result
		
	class Restart(aedsdk.Event):
		def __init__(self):
			pass
		
		def perform(self,time=None):
			self.exe.new_trial()
		
		@classmethod
		def json(cls):
			result = super(Mickey.Restart,cls).json()
			result['color'] = '00ff00'
			return result
	
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
			self.exe.interval_happen('[%f] Begin Wait'%(self.duration),self.name)
			
		def at_end(self):
			aedsdk.Interval.at_end(self)
		
		def meanwhile(self):
			if self.a_LeverPress.detect():
				self.on_LeverPress()
		
		def set_prop(self,name,val):
			if name=="varyby":
				self.varyby = Decimal(val)
		
		@classmethod
		def json(cls):
			result = super(Mickey.Wait,cls).json()
			result['props'].append({'name':'varyby','type':'DEC','default':0.0})
			result['color'] = 'ededed'
			return result
				
			
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
			self.exe.interval_happen('[%f] Begin Tone'%(self.duration),self.name)
		
		def at_end(self):
			aedsdk.Interval.at_end(self)
			
		def meanwhile(self): pass
		
		def set_prop(self,name,val):
			if name=="varyby":
				self.varyby = Decimal(val)
		
		@classmethod
		def json(cls):
			result = super(Mickey.Tone,cls).json()
			result['props'].append({'name':'varyby','type':'DEC','default':0.0})
			result['color'] = '99FF99'
			return result	
	
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
			self.exe.interval_happen('[%f] Begin Present'%(self.duration),self.name)
		
		def at_end(self):
			aedsdk.Interval.at_end(self)		
		
		def on_LeverPress(self):
			for act in self.events_LeverPress:
				act.perform()
				
		def meanwhile(self):
			if self.a_LeverPress.detect():
				self.on_LeverPress()
		
		def set_prop(self,name,val):
			if name=="varyby":
				self.varyby = Decimal(val)
		
		@classmethod
		def json(cls):
			result = super(Mickey.Present,cls).json()
			result['props'].append({'name':'varyby','type':'DEC','default':0.0})
			result['color'] = 'FF99CC'
			return result
	
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
			self.exe.interval_happen('[%f] Begin Refrain'%(self.duration),self.name)
		
		def at_end(self):
			if self.reward:
				aedsdk.Interval.at_end(self)
			else:
				pass
		
		def on_LeverPress(self):
			self.reward = False
			for act in self.events_LeverPress:
				act.perform()
				
		def meanwhile(self):
			if self.a_LeverPress.detect():
				self.on_LeverPress()
				
		def set_prop(self,name,val):
			if name=="varyby":
				self.varyby = Decimal(val)
		
		@classmethod
		def json(cls):
			result = super(Mickey.Refrain,cls).json()
			result['props'].append({'name':'varyby','type':'DEC','default':0.0})
			result['color'] = 'FFFF99'
			return result	