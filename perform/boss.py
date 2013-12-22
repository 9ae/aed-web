'''
Created on Nov 26, 2013

@author: ari
'''

from decimal import Decimal
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

from models import Experiment, Trial, Happening, RuntimeCache, EmulateAction, SimEvent
import edit.models as em

import aedsdk

from exe import Executioner
import writers as w
from helpers import import_mod_file, poke_cache
from threading import Lock
import libarian

class Dictator(object):
    executioner = None
    experiment = None
    eventObjects = None
    
    def __init__(self,protocol,nickname):
        dt = datetime.now()
        self.experiment = Experiment(name=nickname,protocol=protocol,time_start=dt)
        self.experiment.save()
        self.executioner = Executioner() 
        libarian.init_db_cache(self.experiment)
        # self.lock = Lock()
    
    def current_trial(self):
        return poke_cache(str(self.experiment.id)+'.trial_current',self.experiment.current_trial(),secs=60)
    
    def start(self):
        self.executioner.start()
    
    def complete(self):
        current_trial = self.experiment.current_trial()
        if current_trial!=None:
            current_trial.duration = libarian.time_since_trial(self.experiment.id)
            current_trial.save()
        self.experiment.total_duration = libarian.time_since_exp(self.experiment.id)
        self.experiment.set_trials_completed()
        self.experiment.time_complete = datetime.now()
        self.experiment.save()
        # libarian.clear_db_cache()

    def new_trial(self):
        total_time = libarian.time_since_exp(self.experiment.id)
        trial_time = libarian.time_since_trial(self.experiment.id)
        new_trial = Trial(experiment=self.experiment, duration=Decimal(0.0),completed=False,time_start=datetime.now())
        new_trial.save()
        old_trial = libarian.get_trial_current(self.experiment.id)
        if old_trial!=None:
            w.NextTrialThread(old_trial,new_trial,trial_time,total_time,self.experiment).start()
        else:
            w.NewHappening('TRL','New Trial',total_time,self.experiment).start()
        libarian.set_trial_current(new_trial,self.experiment.id)
        self.executioner.interval_pointer = 0
        self.executioner.is_new_trial = True
        libarian.set_interval_start(datetime.now(),self.experiment.id)
    
    def check_emulate_action(self,action_type):
        if em.Action.objects.filter(type=action_type).count()==1:
            act = em.Action.objects.filter(type=action_type)[0]
            try:
                ea =  EmulateAction.objects.filter(experiment=self.experiment, action=act).latest('id')
                self.action_happen('%s'%(action_type),action_type,ea.time_occurred)
                ea.delete()
                return True
            except ObjectDoesNotExist:
                return False
        else:
            return False
    
    def run_simulate_events(self):
        event_ids = SimEvent.objects.filter(experiment=self.experiment)
        for se in event_ids:
            self.eventObjects[se.eventid].perform(time=se.time_occurred)
        event_ids.delete()    
    
    def action_happen(self,description,keyname,given_time=None):
        if given_time==None:
            time = libarian.time_since_exp(self.experiment.id)
        else:
            time = given_time
        thready = w.NewHappening('ACT',keyname,description,time,self.experiment)
        thready.start()
        
    def event_happen(self,description,keyname,given_time=None):
        if given_time==None:
            time = libarian.time_since_exp(self.experiment.id)
        else:
            time = given_time
        thready = w.NewHappening('EVT',keyname,description,time,self.experiment)
        thready.start()
        
    def interval_happen(self,description,keyname):
        time = libarian.time_since_exp(self.experiment.id)
        thready = w.NewHappening('ITL',keyname,description,time,self.experiment)
        thready.start()

def setup_experiement(db_protocol,delta_ivals):
    loading_error = False
    db_paradigm = db_protocol.paradigm
    parad = import_mod_file(db_paradigm.file_location)
    if parad!=None:
        paradigm = eval('parad.'+db_paradigm.name+'()')
        paradigm.bind_action_listeners()
    else:
        return None
  
    # make thread
    axe = Dictator(db_protocol,db_protocol.name)
    exe = axe.executioner
    exe.set_dictator(axe)
    paradigm.set_executioner(axe)
    exe.trial_duration = db_protocol.trial_duration
    actions = db_paradigm.actions()
    
    #now start loading events
    events = db_protocol.events()
    mapEvents = {}
    for e in events:
        ev = paradigm.instantiate_name(e.type)
        ev.set_executioner(axe)
        ev.name = e.name
        #set properties
        eprops = e.props.all()
        for prop in eprops:
            ev.set_prop(prop.prop_name, prop.val())
        mapEvents[e.id] = ev
    axe.eventObjects = mapEvents
    
    update_interval = delta_ivals!=None
    
    # load intervals
    intervals = db_protocol.intervals()
    for i in intervals:
        it = paradigm.instantiate_name(i.type)
        it.set_executioner(axe)
        it.name = i.name
        if update_interval:
            imap = delta_ivals[str(i.id)]
            it.init_duration(imap['duration'])
            props_count = len(imap['props'])
            ip = 0
            while ip<props_count:
                iprop = imap['props'][ip]
                it.set_prop(iprop['prop_name'],iprop['prop_val'])
                ip = ip + 1
        else:
            it.init_duration(i.duration)
            iprops = i.props.all()
            # set properties
            for prop in iprops:
                it.set_prop(prop.prop_name,prop.val())
        # set begin events
        for b in i.beginEvents():
            try:
                bev = mapEvents[b.event.id]
                it.events_begin.append(bev)
            except KeyError:
                loading_error = True
                break
            
        # set end events
        for ed in i.endEvents():
            try:
                edev = mapEvents[ed.event.id]
                it.events_end.append(edev)
            except KeyError:
                loading_error = True
                break
        
        # set action events
        for act in actions:
            callname = 'events_'+act.type
            action_chain = i.actionEvents(act)
            itachain = []
            for linka in action_chain:
                try:
                    aev = mapEvents[linka.event.id]
                    itachain.append(aev)
                except KeyError:
                    loading_error = True
                    break
            if loading_error:
                break
            it.__setattr__(callname,itachain)
        
        if loading_error:
            break
        it.register_actions(paradigm)
        exe.intervals.append(it)
        
    if loading_error:
        return None
    else:
        axe.start()
        return axe.experiment

