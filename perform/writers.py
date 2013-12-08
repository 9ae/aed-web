'''
Created on Nov 26, 2013

@author: ari
'''
from decimal import Decimal
from threading import Thread
from models import Experiment, Trial, Happening

import libarian

class NextTrialThread(Thread):
    def __init__(self,old_trial,new_trial,trial_time,total_time):
        Thread.__init__(self)
        self.old_trial=old_trial
        self.new_trial=new_trial
        self.total_time = total_time
        self.trial_time = trial_time
    
    def run(self):
        self.old_trial.completed=True
        self.old_trial.duration = self.trial_time
        self.old_trial.save()
        hap = Happening(trial=self.new_trial, time_occurred=self.total_time, type='TRL', description='New Trial')
        hap.save()
        libarian.cache_happening(hap,self.new_trial.experiment.id)

class NewHappening(Thread):
    def __init__(self,htype,descript,time,exp_id):
        Thread.__init__(self)
        self.trial=libarian.get_trial_current(exp_id)
        self.type=htype
        self.desription=descript
        self.time=time
        self.experiment_id = exp_id
    
    def run(self):
        if self.trial==None:
            return
        else:
            hap = Happening(trial=self.trial, time_occurred=self.time, type=self.type, description=self.desription)
            hap.save()
            print '%s @ %f'%(self.desription,self.time)
            libarian.cache_happening(hap,self.experiment_id)

class MarkHappening(Thread):
    def __init__(self,hap_id):
        Thread.__init__(self)
        self.hap_id=hap_id
    
    def run(self):
        hap = Happening.objects.get(id=self.hap_id)
        hap.broadcast = True
        hap.save()