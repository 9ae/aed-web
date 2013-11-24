from django.db import models
import janus

class Experiment(models.Model):
    time_start = models.TimeField()
    time_complete = models.TimeField(null=True, blank=True)
    trials_completed = models.IntegerField(default=0)
    total_duration = models.DecimalField(max_digits=8, decimal_places=3,null=True, blank=True)
    name= models.CharField(max_length=255)
    '''
    def create(self):
        self.intervals = []
        self.events = []    
        self.tk = janus.Timekeeper(-3)
        
        self.interval_pointer = 0
        self.is_new_trial = False
    
    def new_trial(self):
        self.interval_pointer = 0
        self.tk.new_trial()
        self.is_new_trial = True
        
    def trials_count(self):
        return len(self.tk.timelog)
    
    def loop(self):
        # check time
        
        trial_time = self.tk.trial_diff()
        current_interval = self.intervals[self.interval_pointer]
        
        if self.is_new_trial:
            current_interval.at_begin()
            self.is_new_trial = False
        
        if trial_time>current_interval.duration:
            # go to next interval
            current_interval.at_end()
            self.interval_pointer = self.interval_pointer + 1
            if self.interval_pointer >= len(self.intervals):
                # is at last interval
                self.new_trial()
                return
            # start new interval
            next_interval = self.intervals[self.interval_pointer]
            next_interval.at_begin()
            next_interval.meanwhile()
        else:
            current_interval.meanwhile()
            

    def print_details(self):
        print '%s '%(self.name)
        print '\t created on: %s'%self.created_on
        
        print '\n Events'
        for e in self.events:
            print e
        
        print '\n Intervals'
        for i in self.intervals:
            print i
    '''
class Trial(models.Model):
    experiment = models.ForeignKey(Experiment)
    time_start = models.TimeField()
    duration = models.DecimalField(max_digits=8, decimal_places=3,null=True, blank=True)
    completed = models.BooleanField()

class Happening(models.Model):
    trial = models.ForeignKey(Trial)
    trial_time_occurred = models.DecimalField(max_digits=8, decimal_places=3)
    name = models.CharField(max_length=16)
