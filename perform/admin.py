'''
Created on Oct 24, 2013

@author: alice
'''
from django.contrib import admin
import models
admin.site.register(models.Experiment)
admin.site.register(models.Trial)
admin.site.register(models.Happening)
admin.site.register(models.RuntimeCache)