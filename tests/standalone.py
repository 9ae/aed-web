'''
Created on Nov 26, 2013

@author: ari
'''
'''
from threading import Thread
class Wind(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.i = 0
    
    def run(self):
        while self.i<1000:
            print 'at %d'%self.i
            self.i = self.i + 1
        print "done"
    
    def bother(self):
        self.i = 1000
        print 'big step up'

wind = Wind()
wind.start()
wind.bother()
'''

import perform.janus as j
tk = j.Timekeeper(3)

i = 0
while i<1e6:
    if i%100==0:
        print tk.diff()
    i = i +1
