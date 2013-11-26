'''
Created on Nov 26, 2013

@author: ari
'''
import models
import edit.models as em
import aedsdk
from exe import Executioner

def setupExperiement(paradigm,db_protocol):
    # make thread
    exe = Executioner(nickname=db_protocol.name)
    paradigm.set_executioner(exe)
    
    #now start loading events
    events = em.Event.objects.filter(protocol=db_protocol)
    for e in events:
        ev = paradigm.instantiate_name(e.type)

    exe.start()
    return exe.exp