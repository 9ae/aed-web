'''
Created on Nov 24, 2013

@author: ari
'''
from django.contrib import admin
from models import Paradigm, Protocol,Interval,Event,Action, IntervalProperty,EventProperty,ActionProperty

admin.site.register(Paradigm)
admin.site.register(Protocol)
admin.site.register(Interval)
admin.site.register(Event)
admin.site.register(Action)
admin.site.register(IntervalProperty)
admin.site.register(EventProperty)
admin.site.register(ActionProperty)