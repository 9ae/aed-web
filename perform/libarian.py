'''
Created on Nov 28, 2013

@author: ari
'''
from models import RuntimeCache

from helpers import poke_cache
def clear_db_cache():
    from django.core.cache import cache
    RuntimeCache.objects.all().delete()
    cache.clear()


def init_db_cache(experiment):
    from django.core.cache import cache
    runcache = RuntimeCache(experiment_current=experiment,experiment_terminate=False)
    runcache.save()
    cache.set('experiment_current',experiment)
    cache.set('experiment_terminate',False)


def get_experiment_current():
    def from_db():
        # since there is only one entry in the db, we can just always get the latest
        rtc = RuntimeCache.objects.latest('id')
        return rtc.experiment_current
    return poke_cache('experiment_current',from_db,secs=600)

def get_experiment_terminate():
    def from_db():
        rtc = RuntimeCache.objects.latest('id')
        return rtc.experiment_terminate
    return poke_cache('experiment_terminate',from_db,secs=600)


def set_experiment_terminate():
    from django.core.cache import cache
    rtc = RuntimeCache.objects.latest('id')
    cache.set('experiment_terminate',True,60)
    rtc.experiment_terminate = True
    rtc.save()

def get_trial_current():
    return poke_cache('trial_current',get_experiment_current().current_trial,secs=60)

def set_trial_current(trial):
    from django.core.cache import cache
    cache.set('trial_current',trial,60)
