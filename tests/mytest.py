'''
Created on Nov 26, 2013

@author: ari
'''
from threading import Thread
import models
import logging

logger = logging.getLogger('mytest')

class TriadFinder(Thread):
    def __init__(self):
        Thread.__init__(self)
        
    def run(self):
        i = 3;
        while i<1000:
            if i%3==0:
                models.Triad(number=i).save()
            i = i+1
        logger.info('thread complete')

def checkTriadComplete():
    from django.db.models import Max
    result_map = models.Triad.objects.all().aggregate(Max('number'))
    if result_map['number__max']==999:
        return True
    else:
        return False
    