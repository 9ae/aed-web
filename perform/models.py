from django.db import models
from edit.models import Protocol

class Experiment(models.Model):
    time_start = models.TimeField(auto_now_add=True)
    time_complete = models.TimeField(null=True, blank=True, auto_now=True)
    trials_completed = models.IntegerField(default=0)
    total_duration = models.DecimalField(max_digits=8, decimal_places=3,null=True, blank=True)
    name = models.CharField(max_length=255)
    protocol = models.ForeignKey(Protocol)

class Trial(models.Model):
    experiment = models.ForeignKey(Experiment)
    time_start = models.TimeField()
    duration = models.DecimalField(max_digits=8, decimal_places=3,null=True, blank=True)
    completed = models.BooleanField()

class Happening(models.Model):
    trial = models.ForeignKey(Trial)
    trial_time_occurred = models.DecimalField(max_digits=8, decimal_places=3)
    type = models.CharField(max_length=3, choices=(('ACT','Action Occurred'),('EVT','Event Occurred'),('ITL','Interval Start'),('TRL','Trial Start')) )
    description = models.TextField()
