from __future__ import unicode_literals
from django.db import models


class Publication(models.Model):
    publication = models.TextField()
    def __unicode__(self):
        return self.publication

class Experiment(models.Model):
    experiment = models.TextField()
    def __unicode__(self):
        return self.experiment

class Variable(models.Model):
    variable = models.TextField()
    def __unicode__(self):
        return self.variable

class Frequency(models.Model):
    frequency = models.TextField()
    def __unicode__(self):
        return self.frequency

class Ensemble(models.Model):
    ensemble = models.TextField()
    def __unicode__(self):
        return self.ensemble

class Keyword(models.Model):
    keyword = models.TextField()
    def __unicode__(self):
        return self.keyword

