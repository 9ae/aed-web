'''
Created on Nov 28, 2013

@author: ari
'''
from datetime import datetime
from decimal import Decimal

from models import RuntimeCache, Happening
from django.core import serializers
from django.core.cache import cache
from helpers import millisec

from helpers import poke_cache

''' may be depreciated
def clear_db_cache():
    RuntimeCache.objects.all().delete()
    cache.clear()
'''

def init_db_cache(experiment):
    runcache = RuntimeCache(experiment=experiment,experiment_terminate=False)
    runcache.save()
    cache.set(str(experiment.id)+'.experiment',experiment)
    cache.set(str(experiment.id)+'.experiment_terminate',False)


def get_experiment_current(exp_id):
    def from_db():
        # since there is only one entry in the db, we can just always get the latest
        rtc = RuntimeCache.objects.filter(experiment_id__exact=exp_id)
        return rtc.experiment
    return poke_cache(str(exp_id)+'.experiment_current',from_db,secs=600)

def get_experiment_terminate(exp_id):
    def from_db():
        rtc = RuntimeCache.objects.filter(experiment_id__exact=exp_id)
        return rtc.experiment_terminate
    return poke_cache(str(exp_id)+'.experiment_terminate',from_db,secs=600)


def set_experiment_terminate(exp_id):
    rtc = RuntimeCache.objects.filter(experiment_id__exact=exp_id)
    cache.set(str(exp_id)+'.experiment_terminate',True,60)
    rtc.experiment_terminate = True
    rtc.save()

def get_trial_current(exp_id):
    return poke_cache(str(exp_id)+'.trial_current',get_experiment_current(exp_id).current_trial,secs=60)

def set_trial_current(trial,exp_id):
    cache.set(str(exp_id)+'.trial_current',trial,60)

def get_happenings(exp_id):
    def from_db():
        if RuntimeCache.objects.count()>0:
            rtc = RuntimeCache.objects.filter(experiment_id__exact=exp_id)
            return rtc.happening_ids
        else:
            return ''
    return poke_cache(str(exp_id)+'.happening_ids',from_db,secs=30)

def clear_happenings(exp_id):
    rtc = RuntimeCache.objects.filter(experiment_id__exact=exp_id)
    rtc.happening_ids = ''
    rtc.save()
    cache.set('happening_ids','',40)

def cache_happening(happening,exp_id):
    happening_ids = get_happenings(exp_id)
    
    # add to haps list
    if happening_ids=='':
        happening_ids = str(happening.id)
    else:
        happening_ids = happening_ids+','+str(happening.id)
    
    # make happening serialized
    happening_str = serializers.serialize('json',[happening])
    happening_str = happening_str.strip('[]')
    hap_key = str(exp_id)+'.H.'+str(happening.id)
    
    #place list to rtc
    rtc = RuntimeCache.objects.filter(experiment_id__exact=exp_id)
    rtc.happeing_ids = happening_ids
    rtc.save()
    
    #put in cache
    cache.set(str(exp_id)+'.happening_ids',happening_ids,30)
    cache.set(hap_key,happening_str,60)
    
def get_happening_by_id(hap_id,exp_id):
    hap_key = str(exp_id)+'.H.'+str(hap_id)
    hap_str = cache.get(hap_key)
    if hap_str:
        hap = Happening.objects.get(id=hap_id)
        hap_str = serializers.serialize('json',[hap])
        hap_str = hap_str.strip('[]')
    else:
        cache.delete(hap_key)
    return hap_str

def time_start_exp(exp_id):
    def from_db():
        rtc = RuntimeCache.objects.filter(experiment_id__exact=exp_id)
        #print 'exp start=%s'%rtc.experiment_current.time_start
        return rtc.experiment_current.time_start
    return poke_cache(str(exp_id)+'.time_start_exp',from_db,secs=1800)

def time_start_trial(exp_id):
    def from_db():
        rtc = RuntimeCache.objects.filter(experiment_id__exact=exp_id)
        exp = rtc.experiment
        trial = exp.current_trial()
        if trial==None:
            #print 'trial undefined finding experiment time'
            return time_start_exp()
        else:
            #print 'trial start=%s'%trial.time_start
            return trial.time_start
    return poke_cache(str(exp_id)+'.time_start_trial',from_db,secs=100)

def time_since_exp(exp_id):
    exp_start = time_start_exp(exp_id)
    diff = datetime.now() - exp_start
    return millisec(diff)

def time_since_trial(exp_id):
    trial_start = time_start_trial(exp_id)
    diff = datetime.now() - trial_start
    return millisec(diff)

def time_since_interval(exp_id):
    def from_db():
        rtc = RuntimeCache.objects.filter(experiment_id__exact=exp_id)
        return rtc.interval_start
    int_start = poke_cache(str(exp_id)+'.interval_start',from_db,secs=30)
    if int_start==None:
        return Decimal(0.000)
    else:
        diff = datetime.now() - int_start
        return millisec(diff)

def set_interval_start(dt,exp_id):
    cache.set(str(exp_id)+'.interval_start',dt,30)
    rtc = RuntimeCache.objects.filter(experiment_id__exact=exp_id)
    rtc.interval_start = dt
    rtc.save()
