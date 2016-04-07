from django.db import models
from django.contrib.auth.models import User

AUTHOR_TITLE_CHOICE = (
            (0, 'Dr'),
            (1, 'Hon'),
            (2, 'Miss'),
            (3, 'Mr'),
            (4, 'Mrs'),
            (5, 'Ms'),
            (6, 'Prof'),
            (7, 'Sir'),
            (8, 'Knight'),
            (9, ' '),
            )

PUBLICATION_TYPE_CHOICE = (
            (0, 'Book'),
            (1, 'Conference'),
            (2, 'Journal'),
            (3, 'Magazine'),
            (4, 'Poster'),
            (5, 'Presentation'),
            (6, 'Technical Report'),
            (7, 'Other'),
            )

PUBLICATION_STATUS_CHOICE = (
            (0, 'Published'),
            (1, 'Submitted'),
            (2, 'Accepted'),
            (3, 'Not Applicable'),
            )            
class Experiment(models.Model):
    experiment = models.TextField()
    def __str__(self):
        return self.experiment
        
class Frequency(models.Model):
    frequency = models.TextField()
    def __str__(self):
        return self.frequency
        
class Keyword(models.Model):
    keyword = models.TextField()
    def __str__(self):
        return self.keyword  
        
class Model(models.Model):
    model = models.TextField() 
    ensumble = models.TextField()
    def __str__(self):
        return self.model              

class Variable(models.Model):
    variable = models.TextField()    
    def __str__(self):
        return self.variable

class Project(models.Model):
    project = models.TextField()
    def __str__(self):
        return self.project

class Funding(models.Model):
    funding = models.TextField()
    def __str__(self):
        return self.funding

class Author(models.Model):
    
    title = models.IntegerField(choices=AUTHOR_TITLE_CHOICE, default=9)
    first_name = models.TextField()
    middle_name = models.TextField()
    last_name = models.TextField()
    institution = models.TextField()
    email = models.EmailField(max_length=128)
    def __str__(self) :
        return " ".join((AUTHOR_TITLE_CHOICE[int(self.title)][1], self.first_name, self.middle_name, self.last_name))

class Publication(models.Model):

   
    publication_type = models.IntegerField(choices=PUBLICATION_TYPE_CHOICE, default=2)
    status = models.IntegerField(choices=PUBLICATION_STATUS_CHOICE, default=0)
    submitter = models.ForeignKey(User) 
    title = models.TextField()
    projects = models.ManyToManyField(Project)
    funding = models.ManyToManyField(Funding)
    project_number = models.TextField()
    task_number = models.TextField()
    authors = models.ManyToManyField(Author)
    publication_date = models.DateField()
    url = models.URLField()
    doi = models.TextField()
    abstract = models.TextField()
    experiments = models.ManyToManyField(Experiment)
    frequency = models.ManyToManyField(Frequency)
    keywords = models.ManyToManyField(Keyword)
    model = models.ManyToManyField(Model)
    variables = models.ManyToManyField(Variable)
    def __str__(self):
        return self.title
    
class Book(models.Model):
    publication_id = models.ForeignKey(Publication)
    book_name = models.TextField()
    chapter_title = models.TextField()
    start_page = models.TextField()
    end_page = models.TextField()
    editor = models.TextField()
    city_of_publication  = models.TextField()
    publisher = models.TextField()
    def __str__(self):
        return self.book_name
        
class Conference(models.Model):
    publication_id = models.ForeignKey(Publication)
    conference_name = models.TextField()
    conference_serial_number = models.TextField()
    event_location = models.TextField()
    start_page = models.TextField()
    end_page = models.TextField()
    editor = models.TextField()
    city_of_publication  = models.TextField()
    publisher = models.TextField()
    def __str__(self):
        return self.conference_name

class Journal(models.Model):
    publication_id = models.ForeignKey(Publication)
    journal_name = models.TextField()
    editor = models.TextField()
    volume_number = models.TextField()
    artical_number = models.TextField()
    start_page = models.TextField()
    end_page = models.TextField()
    def __str__(self):
        return self.journal_name        

class Magazine(models.Model):
    publication_id = models.ForeignKey(Publication)
    magazine_name = models.TextField()
    editor = models.TextField()
    volume_number = models.TextField()
    artical_number = models.TextField()
    start_page = models.TextField()
    end_page = models.TextField()
    def __str__(self):
        return self.magazine_name 
        
class Poster(models.Model):
    publication_id = models.ForeignKey(Publication)
    poster_title = models.TextField()
    event = models.TextField()
    def __str__(self):
        return self.poster_title 
        
class Presentation(models.Model):
    publication_id = models.ForeignKey(Publication)
    presentation_title = models.TextField()
    def __str__(self):
        return self.presentation_title 
        
class Technical_Report(models.Model):
    publication_id = models.ForeignKey(Publication)
    report_number = models.TextField()
    editor = models.TextField()
    issuer = models.TextField()   
    def __str__(self):
        return self.title 
        
class Other(models.Model):
    publication_id = models.ForeignKey(Publication)
    other_pub = models.TextField()
    def __str__(self):
        return self.other_pub                               