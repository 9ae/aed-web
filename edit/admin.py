'''
Created on Nov 24, 2013

@author: ari
'''
from django.contrib import admin
from models import *

admin.site.register(Paradigm)
admin.site.register(Protocol)
admin.site.register(Interval)
admin.site.register(Event)
admin.site.register(Action)
'''
admin.site.register(IntervalProperty)
admin.site.register(EventProperty)
admin.site.register(ActionProperty)
'''
admin.site.register(AIEProperty)
admin.site.register(IntervalBegin)
admin.site.register(IntervalEnd)
admin.site.register(IntervalAction)