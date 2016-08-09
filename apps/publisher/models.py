from django.db import models as django_models
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


class Experiment(django_models.Model):
    experiment = django_models.TextField()

    def __str__(self):
        return self.experiment


class Frequency(django_models.Model):
    frequency = django_models.TextField()

    def __str__(self):
        return self.frequency


class Keyword(django_models.Model):
    keyword = django_models.TextField()

    def __str__(self):
        return self.keyword


class Model(django_models.Model):
    model = django_models.TextField()

    def __str__(self):
        return self.model


class Variable(django_models.Model):
    variable = django_models.TextField()

    def __str__(self):
        return self.variable


class Project(django_models.Model):
    project = django_models.TextField()
    variables = django_models.ManyToManyField(Variable)
    frequencies = django_models.ManyToManyField(Frequency)
    models = django_models.ManyToManyField(Model)
    experiments = django_models.ManyToManyField(Experiment)
    keywords = django_models.ManyToManyField(Keyword)

    def __str__(self):
        return self.project


class JournalOptions(django_models.Model):
    journal_name = django_models.TextField()

    def __unicode__(self):
        return '%s' % (self.journal_name)


class Funding(django_models.Model):
    funding = django_models.TextField()

    def __str__(self):
        return self.funding


class Author(django_models.Model):
    name = django_models.TextField()
    institution = django_models.TextField(blank=True)

    def __unicode__(self):
        return self.name


class Publication(django_models.Model):
    publication_type = django_models.IntegerField(choices=PUBLICATION_TYPE_CHOICE, default=2)
    status = django_models.IntegerField(choices=PUBLICATION_STATUS_CHOICE, default=0)
    submitter = django_models.ForeignKey(User)
    title = django_models.TextField()
    projects = django_models.ManyToManyField(Project)
    funding = django_models.ManyToManyField(Funding)
    project_number = django_models.TextField()
    task_number = django_models.TextField()
    authors = django_models.ManyToManyField(Author, blank=False)
    publication_date = django_models.DateField()
    url = django_models.URLField()
    doi = django_models.TextField(blank=True)
    abstract = django_models.TextField()
    experiments = django_models.ManyToManyField(Experiment)
    frequency = django_models.ManyToManyField(Frequency)
    keywords = django_models.ManyToManyField(Keyword)
    model = django_models.ManyToManyField(Model, through='PubModels')
    variables = django_models.ManyToManyField(Variable)

    def __unicode__(self):
        return self.title

    @property
    def get_publication_type(self):
        return PUBLICATION_TYPE_CHOICE[int(self.publication_type)][1]

    @property
    def get_status(self):
        return PUBLICATION_STATUS_CHOICE[int(self.status)][1]

    @property
    def get_year(self):
        return self.publication_date.year

    @property
    def get_authors(self):
        # return self.authors.first()
        count = self.authors.count()
        authors = self.authors.all().order_by('id')
        if count > 2:
            return "{0}, {1}, et al.".format(str(authors[0]), str(authors[1]))
        elif count == 2:
            return "{0}, {1}".format(str(authors[0]), str(authors[1]))
        elif count == 1:
            return str(authors[0])
        else:
            return ''


class PubModels(django_models.Model):
    publication = django_models.ForeignKey(Publication)
    model = django_models.ForeignKey(Model)
    ensemble = django_models.IntegerField()


class Book(django_models.Model):
    publication_id = django_models.ForeignKey(Publication)
    book_name = django_models.TextField()
    chapter_title = django_models.TextField(blank=True)
    start_page = django_models.TextField(blank=True)
    end_page = django_models.TextField(blank=True)
    editor = django_models.TextField(blank=True)
    city_of_publication = django_models.TextField(blank=True)
    publisher = django_models.TextField(blank=True)

    def __str__(self):
        return self.book_name


class Conference(django_models.Model):
    publication_id = django_models.ForeignKey(Publication)
    conference_name = django_models.TextField()
    conference_serial_number = django_models.TextField(blank=True)
    event_location = django_models.TextField(blank=True)
    start_page = django_models.TextField(blank=True)
    end_page = django_models.TextField(blank=True)
    editor = django_models.TextField(blank=True)
    city_of_publication = django_models.TextField(blank=True)
    publisher = django_models.TextField(blank=True)

    def __str__(self):
        return self.conference_name


class Journal(django_models.Model):
    publication_id = django_models.ForeignKey(Publication)
    journal_name = django_models.ForeignKey(JournalOptions)
    volume_number = django_models.TextField(blank=True)
    article_number = django_models.TextField(blank=True)
    start_page = django_models.TextField(blank=True)
    end_page = django_models.TextField(blank=True)

    def __unicode__(self):
        return '%s' % (self.journal_name)


class Magazine(django_models.Model):
    publication_id = django_models.ForeignKey(Publication)
    magazine_name = django_models.TextField()
    editor = django_models.TextField(blank=True)
    volume_number = django_models.TextField(blank=True)
    article_number = django_models.TextField(blank=True)
    start_page = django_models.TextField(blank=True)
    end_page = django_models.TextField(blank=True)

    def __str__(self):
        return self.magazine_name


class Poster(django_models.Model):
    publication_id = django_models.ForeignKey(Publication)
    poster_title = django_models.TextField()
    event = django_models.TextField(blank=True)

    def __str__(self):
        return self.poster_title


class Presentation(django_models.Model):
    publication_id = django_models.ForeignKey(Publication)
    presentation_title = django_models.TextField()

    def __str__(self):
        return self.presentation_title


class TechnicalReport(django_models.Model):
    publication_id = django_models.ForeignKey(Publication)
    report_number = django_models.TextField()
    editor = django_models.TextField(blank=True)
    issuer = django_models.TextField(blank=True)

    def __str__(self):
        return self.report_number


class Other(django_models.Model):
    publication_id = django_models.ForeignKey(Publication)
    other_pub = django_models.TextField()

    def __str__(self):
        return self.other_pub


class AvailableYears(django_models.Model):
    year = django_models.IntegerField()

    def __str__(self):
        return self.year
