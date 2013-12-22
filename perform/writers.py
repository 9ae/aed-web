'''
Created on Nov 26, 2013

@author: ari
'''
from decimal import Decimal
from threading import Thread
from models import Experiment, Trial, Happening

import libarian

class NextTrialThread(Thread):
    def __init__(self,old_trial,new_trial,trial_time,total_time,experiment):
        Thread.__init__(self)
        self.old_trial=old_trial
        self.new_trial=new_trial
        self.total_time = total_time
        self.trial_time = trial_time
        self.experiment=experiment
    
    def run(self):
        hap = Happening(experiment=self.experiment, time_occurred=self.total_time, type='TRL', description='New Trial')
        hap.save()
        libarian.cache_happening(hap,self.new_trial.experiment.id)
        self.old_trial.completed=True
        self.old_trial.duration = self.trial_time
        self.old_trial.save()
        
class NewHappening(Thread):
    def __init__(self,htype,keyname,descript,time,exp):
        Thread.__init__(self)
        self.type=htype
        self.desription=descript
        self.time=time
        self.experiment = exp
        self.keyname = keyname
    
    def run(self):
        hap = Happening(experiment=self.experiment, time_occurred=self.time, type=self.type, description=self.desription, keyname=self.keyname)
        hap.save()
        print '%s @ %f'%(self.desription,self.time)
        libarian.cache_happening(hap,self.experiment.id)

class MarkHappening(Thread):
    def __init__(self,hap_id):
        Thread.__init__(self)
        self.hap_id=hap_id
    
    def run(self):
        hap = Happening.objects.get(id=self.hap_id)
        hap.broadcast = True
        hap.save()