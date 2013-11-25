from django.db import models

class ParadigmProperty(models.Model):
	prop_type = models.CharField(max_length=3,choices=(('INT','Integer'),('STR','String'),('BOO','Boolean'),('DEC','Decimal')))
	prop_name = models.CharField(max_length=100)
	prop_val_int = models.IntegerField(null=True,blank=True)
	prop_val_str = models.TextField(default='',blank=True)
	prop_val_boo = models.BooleanField(default=False)
	prop_val_dec = models.DecimalField(max_digits=8, decimal_places=3,null=True, blank=True)
	
	class Meta:
		abstract = True
		
	def val(self):
		if self.prop_type=='INT':
			return self.prop_val_int
		elif self.prop_type=='STR':
			return self.prop_val_str
		elif self.prop_type=='BOO':
			return self.prop_val_boo
		elif self.prop_type=='DEC':
			return self.prop_val_dec
		else:
			return None

# Create your models here.
class Paradigm(models.Model):
	name = models.CharField(max_length=100)
	file_location = models.FilePathField(path='/Users/ari/slytherin/aed-web/paradigms',match='^[a-zA-Z0-9]*.py')
	created_on=models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return u'[%d] %s' % (self.id, self.name)

class Protocol(models.Model):
	paradigm = models.ForeignKey(Paradigm)
	name = models.CharField(max_length=100)
	trial_duration = models.DecimalField(max_digits=8, decimal_places=3,default=0.0)
	created_on = models.DateTimeField(auto_now_add=True)
	modified_on = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return u'[%d] %s<%s' % (self.id, self.name, self.paradigm.name)

class Interval(models.Model):
	protocol = models.ForeignKey(Protocol)
	order = models.PositiveSmallIntegerField()
	type = models.CharField(max_length=100)
	duration = models.DecimalField(max_digits=8, decimal_places=3,default=0.0)
	name = models.CharField(max_length=100)
	# put actions and events

	def __unicode__(self):
		return u'[%d] %s(%s) < %s' % (self.id, self.name, self.type, self.protocol)

class IntervalProperty(ParadigmProperty):
	interval = models.ForeignKey(Interval)
	
	def __unicode__(self):
		return u'%s[%d].%s'%(self.interval.name,self.interval.id,self.prop_name)

class Action(models.Model):
	paradigm = models.ForeignKey(Paradigm)
	type = models.CharField(max_length=100)

	def __unicode__(self):
		return u'[%d] %s < %s' % (self.id, self.type, self.paradigm.name)

class ActionProperty(ParadigmProperty):
	action = models.ForeignKey(Action)

	def __unicode__(self):
		return u'%s[%d].%s'%(self.action.type,self.action.id,self.prop_name)

class Event(models.Model):
	protocol = models.ForeignKey(Protocol)
	type = models.CharField(max_length=100)
	name = models.CharField(max_length=100)

	def __unicode__(self):
		return u'[%d] %s(%s) < %s' % (self.id, self.name, self.type, self.protocol.name)

class EventProperty(ParadigmProperty):
	event = models.ForeignKey(Event)

	def __unicode__(self):
		return u'%s[%d].%s'%(self.event.name, self.event.id,self.prop_name)
	
class EventsChain(models.Model):
	order = models.PositiveSmallIntegerField()
	event = models.ForeignKey(Event)
	
	class Meta:
		abstract = True

class IntervalBegin(EventsChain):
	interval = models.ForeignKey(Interval)

class IntervalEnd(EventsChain):
	interval = models.ForeignKey(Interval)

class IntervalAction(EventsChain):
	interval = models.ForeignKey(Interval)
	action = models.ForeignKey(Action)