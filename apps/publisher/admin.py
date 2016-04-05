from django.contrib import admin
#from django.db import models
from publisher.models import Keyword, Experiment, Variable, Frequency, Ensemble, Publication


admin.site.register(Keyword)
admin.site.register(Experiment)
admin.site.register(Variable)
admin.site.register(Frequency)
admin.site.register(Ensemble)
admin.site.register(Publication)
