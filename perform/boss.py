'''
Created on Nov 26, 2013

@author: ari
'''
import models
import edit.models as em
import aedsdk
from helpers import import_mod_file
from exe import Executioner

def setupExperiement(db_protocol):
    loading_error = False
    db_paradigm = db_protocol.paradigm
    parad = import_mod_file(db_paradigm.file_location)
    if parad!=None:
        paradigm = eval('parad.'+db_paradigm.name+'()')
        paradigm.bind_action_listeners()
    else:
        return None
  
    # make thread
    exe = Executioner(db_protocol)
    paradigm.set_executioner(exe)
    exe.trial_duration = db_protocol.trial_duration
    actions = db_paradigm.actions()
    
    #now start loading events
    events = db_protocol.events()
    mapEvents = {}
    for e in events:
        ev = paradigm.instantiate_name(e.type)
        ev.set_executioner(exe)
        ev.name = e.name
        #set properties
        eprops = e.props.all()
        for prop in eprops:
            ev.set_prop(prop.prop_name, prop.val())
        mapEvents[e.id] = ev
    exe.events = mapEvents.values()
    
    # load intervals
    intervals = db_protocol.intervals()
    for i in intervals:
        it = paradigm.instantiate_name(i.type)
        it.set_executioner(exe)
        it.name = i.name
        it.duration = i.duration
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
        exe.start()
        return exe.exp