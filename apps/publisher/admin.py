from django.contrib import admin
#from django.db import models
from models import Experiment, Frequency, Keyword, Model, Variable, Project, Funding, Author, Publication, Book, Conference, Journal, Magazine, Poster, Presentation, Technical_Report, Other, Journal_Options

admin.site.register(Experiment)
admin.site.register(Frequency)
admin.site.register(Keyword)
admin.site.register(Model)
admin.site.register(Variable)
admin.site.register(Project)
admin.site.register(Funding)
admin.site.register(Author)
admin.site.register(Publication)
admin.site.register(Book)
admin.site.register(Conference)
admin.site.register(Journal)
admin.site.register(Magazine)
admin.site.register(Poster)
admin.site.register(Technical_Report)
admin.site.register(Other)
admin.site.register(Journal_Options)