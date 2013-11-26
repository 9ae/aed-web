from django.db import models

# Create your models here.


class Triad(models.Model):
    number = models.IntegerField()
    
    def __unicode__(self):
        return u'%d' % (self.number)
