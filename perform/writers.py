'''
Created on Nov 26, 2013

@author: ari
'''
from decimal import Decimal
from threading import Thread
from models import Experiment, Trial, Happening

class NextTrialThread(Thread):
    def __init__(self,exp,time):
        Thread.__init__(self)
        self.exp = exp
        self.time = time
    
    def run(self):
        current_trial = self.exp.current_trial()
        if current_trial!=None:
            current_trial.completed=True
            current_trial.duration = self.time
            current_trial.save()
        new_trial = Trial(experiment=self.exp, duration=Decimal(0.0),completed=False)
        new_trial.save()
        hap = Happening(trial=new_trial, trial_time_occurred=Decimal(0.0), type='TRL', description='New Trial')
        hap.save()
        print 'New Trial @ %f'%self.time

class NewHappening(Thread):
    def __init__(self,trial,type,descript,time):
        Thread.__init__(self)
        self.trial=trial
        self.type=type
        self.desription=descript
        self.time=time
    
    def run(self):
        hap = Happening(trial=self.trial, trial_time_occurred=self.time, type=self.type, description=self.desription)
        hap.save()
        print '%s @ %f'%(self.desription,self.time)