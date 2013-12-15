'''
Created on Nov 26, 2013

@author: ari
'''
from decimal import Decimal
from threading import Thread
from models import Experiment, Trial, Happening

import libarian

class NextTrialThread(Thread):
    def __init__(self,old_trial,new_trial,trial_time,total_time,experiment,lock):
        Thread.__init__(self)
        self.old_trial=old_trial
        self.new_trial=new_trial
        self.total_time = total_time
        self.trial_time = trial_time
        self.experiment=experiment
        self.lock = lock
    
    def run(self):
        self.old_trial.completed=True
        self.old_trial.duration = self.trial_time
        self.old_trial.save()
        self.lock.acquire()
        try:
            hap = Happening(experiment=self.experiment, time_occurred=self.total_time, type='TRL', description='New Trial')
            hap.save()
            libarian.cache_happening(hap,self.new_trial.experiment.id)
        finally:
            self.lock.release()

class NewHappening(Thread):
    def __init__(self,htype,descript,time,exp,lock=None):
        Thread.__init__(self)
        self.type=htype
        self.desription=descript
        self.time=time
        self.experiment = exp
        self.lock = lock
    
    def run(self):
        if self.lock!=None:
            self.lock.acquire()
        try:
            hap = Happening(experiment=self.experiment, time_occurred=self.time, type=self.type, description=self.desription)
            hap.save()
            print '%s @ %f'%(self.desription,self.time)
            libarian.cache_happening(hap,self.experiment.id)
        finally:
            if self.lock!=None:
                self.lock.release()

class MarkHappening(Thread):
    def __init__(self,hap_id):
        Thread.__init__(self)
        self.hap_id=hap_id
    
    def run(self):
        hap = Happening.objects.get(id=self.hap_id)
        hap.broadcast = True
        hap.save()