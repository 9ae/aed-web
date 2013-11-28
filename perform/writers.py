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
        current_trial = libarian.get_trial_current()
        if current_trial!=None:
            current_trial.completed=True
            current_trial.duration = self.trial_time
            current_trial.save()
        hap = Happening(trial=self.new_trial, time_occurred=self.total_time, type='TRL', description='New Trial')
        hap.save()

class NewHappening(Thread):
    def __init__(self,htype,descript,time):
        Thread.__init__(self)
        self.trial=libarian.get_trial_current()
        self.type=htype
        self.desription=descript
        self.time=time
    
    def run(self):
        if self.trial==None:
            return
        else:
            hap = Happening(trial=self.trial, time_occurred=self.time, type=self.type, description=self.desription)
            hap.save()
            print '%s @ %f'%(self.desription,self.time)