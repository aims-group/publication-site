from __future__ import unicode_literals
from django.db import models


class Publication(models.Model):
    publication = models.TextField()
    def __unicode__(self):
        return self.name

class Experiment(models.Model):
    experiment = models.TextField()
    def __unicode__(self):
        return self.name

class Variable(models.Model):
    variable = models.TextField()
    def __unicode__(self):
        return self.name

class Frequency(models.Model):
    frequency = models.TextField()
    def __unicode__(self):
        return self.name

class Ensemble(models.Model):
    ensemble = models.TextField()
    def __unicode__(self):
        return self.name

class Keyword(models.Model):
    keywords = models.TextField()
    def __unicode__(self):
        return self.name
