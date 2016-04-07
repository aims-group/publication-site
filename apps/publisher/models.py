from django.db import models

class Experiments(models.Model):
    EXPERIMENTS_CHOICE = (
    experiment = models.TextField()
    def __str__(self):
        return self.experiment
        
class Frequencies(models.Model):
    frequency = models.TextField()
    def __str__(self):
        return self.frequency
        
class Keywords(models.Model):
    keyword = models.TextField()
    def __str__(self):
        return self.keyword  
        
class Models(models.Model):
    model = models.TextField() 
    ensumble = models.TextField()
    def __str__(self):
        return self.model              

class Variables(models.Model):
    variable = models.TextField()    
    def __str__(self):
        return self.variable

class Projects(models.Model):
    project = models.TextField()
    def __str__(self):
        return self.project

class Funds(models.Model):
    funding = models.TextField()
    def __str__(self):
        return self.funding

class Author(models.Model):
    AUTHOR_TITLE_CHOICE = (
            ('0', 'Dr'),
            ('1', 'Hon'),
            ('2', 'Miss'),
            ('3', 'Mr'),
            ('4', 'Mrs'),
            ('5', 'Ms'),
            ('6', 'Prof'),
            ('7', 'Sir'),
            ('8', 'Knight'),
            ('9', ' '),
            )
    title = models.CharField(max_length=4, choices=AUTHOR_TITLE_CHOICE, default='9')
    first_name = models.TextField()
    middle_name = models.TextField()
    last_name = models.TextField()
    institution = models.TextField()
    email = models.EmailField(max_length=128, blank=True)
    def __str__(self):
        return " ".join((self.title, self.first_name, self.middle_name, self.last_name))

    
class Books(models.Model):
    publication_id = model.ForeignKey(Publications)
    book_name = models.TextField()
    chapter_title = TextField()
    start_page = models.TextField()
    end_page = models.TextField()
    editor = models.TextField()
    city_of_publication  = models.TextField()
    publisher = models.TextField()
    def __str__(self):
        return self.book_name
        
class Conferences(models.Model):
    conference_name = models.TextField()
    conference_serial_number = models.TextField()
    event_location = models.TextField()
    def __str__(self):
        return self.conference_name

class Journals(models.Model):
    JOURNAL_CHOICE = (
            ('00', ' '),
            ('01', 'Aerosol Science and Technology'),
            ('02', 'American Scientist'),
            ('03', 'Applied Mathematics and Computation'),
            ('04', 'Applied Optics'),
            ('05', 'Atmospheric and Oceanic Optics'),
            ('06', 'Atmospheric Chemistry and Physics'),
            ('07', 'Atmospheric Environment'),
            ('08', 'Atmospheric Research'),
            ('09', 'Boundary-Layer Meteorology'),
            ('10', 'Bulletin of the American Meteorological Society'),
            ('11', 'Climate Dynamics'),
            ('12', 'Climatic Change'),
            ('13', 'Contributions to Atmospheric Physics'),
            ('14', 'Advances in Space Research'),
            ('15', 'Dynamics of Atmospheres and Oceans'),
            ('16', 'Earth Interactions'),
            ('17', 'ECMWF Newsletter'),
            ('18', 'Environmental Science & Technology'),
            ('19', 'EOS, Transactions'),
            ('20', 'Fractals'),
            ('21', 'Geophysical Research Letters'),
            ('22', 'Geoscience and Remote Sensing Letters'),
            ('23', 'IEEE Transactions on Geoscience and Remote Sensing'),
            ('24', 'Izvestiya, Atmospheric and Oceanic Physics'),
            ('25', 'Journal of Aerosol Science'),
            ('26', 'Journal of Agriculture and Forest Meteorology'),
            ('27', 'Journal of Applied Meteorology'),
            ('28', 'Journal of Applied Meteorology and Climatology'),
            ('29', 'Journal of Applied Physics'),
            ('30', 'Journal of Atmospheric and Oceanic Technology'),
            ('31', 'Journal of Climate'),
            ('32', 'Journal of Geophysical Research'),
            ('33', 'Journal of Geophysical Research-Atmospheres'),
            ('34', 'Journal of Hydrometeorology'),
            ('35', 'Journal of Molecular Structure'),
            ('36', 'Journal of Quantitative Spectroscopy & Radiative Transfer'),
            ('37', 'Journal of the Atmospheric Sciences'),
            ('38', 'Meteorology and Atmospheric Physics'),
            ('39', 'Monthly Weather Review'),
            ('40', 'Nature'),
            ('41', 'Nonlinear Processes in Geophysics'),
            ('42', 'Nuclear Science Engineering'),
            ('43', 'Physical Review Letters'),
            ('44', 'Physics and Chemistry of the Earth'),
            ('45', 'Physics Today'),
            ('46', 'Proceedings of the National Academy of Sciences'),
            ('47', 'Quarterly Journal Royal Meteorological Society'),
            ('48', 'Radio Science'),
            ('49', 'Remote Sensing Environment'),
            ('50', 'Science'),
            ('51', 'Scientific American'),
            ('52', 'Tellus'),
            ('53', 'Terrestrial, Atmospheric and Oceanic Sciences'),
            ('54', 'Weather and Forecasting'),
            ('55', 'Acta Meteorologica Sinica'),
            ('56', 'Advances in Atmospheric Sciences'),
            ('57', 'Advances in Geosciences'),
            ('58', 'Advances in Meteorology'),
            ('59', 'Atmosphere'),
            ('60', 'Atmospheric Science Letters'),
            ('61', 'Australian Meteorological and Oceanographic Journal'),
            ('62', 'Biogeosciences'),
            ('63', 'Biogeosciences Discussions'),
            ('64', 'Chines Science bulletin'),
            ('65', 'Climate of the Past'),
            ('66', 'Climate of the Past Discussions'),
            ('67', 'Climate Research'),
            ('68', 'Current Science'),
            ('69', 'Deep Sea Research'),
            ('70', 'Earth and Planetary Science Letters'),
            ('71', 'Earth System Dynamics'),
            ('72', 'Environmental Research Letters'),
            ('73', 'Geoscientific Model Development'),
            ('74', 'Geoscientific Model Development Discussions'),
            ('75', 'Global Biogeochemical Cycles'),
            ('76', 'Global Change Biology'),
            ('77', 'Hydrology and Earth System Sciences'),
            ('78', 'Hydrology and Earth System Sciences Discussions'),
            ('79', 'International Journal of Climatology'),
            ('80', 'Journal of Advances in Modeling Earth Systems'),
            ('81', 'Journal of Biogeography'),
            ('82', 'Journal of Atmopspheric Sciences'),
            ('83', 'Journal of the Meteorological Society of Japan'),
            ('84', 'Local Environment'),
            ('85', 'Molecular Ecology'),
            ('86', 'Nature Climate Change'),
            ('87', 'Nature Geoscience'),
            ('88', 'Ocean Modelling'),
            ('89', 'Palaeogeography, Palaeoclimatology, Palaeoecology'),
            ('90', 'Quaternary Science Reviews'),
            ('91', 'Remote Sensing'),
            ('92', 'Reviews of Geophysics'),
            ('93', 'SOLA'),
            ('94', 'The Cryosphere'),
            ('95', 'The Cryosphere Discussions'),
            ('96', 'The Holocene'),
            ('97', 'Theoretical and Applied Climatology'),
            ('98', 'Water Resources Research'),
            ('99', 'Other'),
            )
    journal_name = models.CharField(max_length=2, choices=JOURNAL_CHOICE, default='00')
    other = models.TextField()
        def __str__(self):
        return self.title        

class Magazines(models.Model):
        magazine_name = models.TextField()
        def __str__(self):
        return self.magazine_name 
        
class Posters(models.Model):
    title = models.TextField()
        def __str__(self):
        return self.title 
        
 class Presentation(models.Model):
    title = models.TextField()
        def __str__(self):
        return self.title 
        
class Technical_Report(models.Model):
    title = models.TextField()
        def __str__(self):
        return self.title 
        
class Other(models.Model):
    title = models.TextField()
        def __str__(self):
        return self.title                               

class Publications(models.Model):
    PUBLICATION_TYPE_CHOICE = (
            ('0', 'Book'),
            ('1', 'Conference'),
            ('2', 'Journal'),
            ('3', 'Magazine'),
            ('4', 'Poster'),
            ('5', 'Presentation'),
            ('6', 'Technical Report'),
            ('7', 'Other'),
            )

    PUBLICATION_STATUS_CHOICE = (
            ('0', 'Published'),
            ('1', 'Submitted'),
            ('2', 'Accepted'),
            ('3', 'Not Applicable'),
            )
   
    publication_type = models.CharField(max_length=1, choices=PUBLICATION_TYPE_CHOICE, default='2')
    status = models.CharField(max_length=1, choices=PUBLICATION_STATUS_CHOICE, default='0')
    
    submitter = models.ForeignKey(User, related_name="publication_submitter")
    
    title = models.CharField(max_length=2048, blank=True)
    projects = models.ManyToManyField(Projects, blank=True)
    funding = models.ManyToManyField(Funding, blank=True)
    project_number = models.CharField(max_length=512, blank=True)
    task_number = models.CharField(max_length=512, blank=True)
    authors = models.ManyToManyField(Author, blank=True)
    publication_date = models.DateField(blank=True, null=True)
    url = models.URLField(blank=True)
    doi = models.CharField(max_length=2048, blank=True)
    abstract = models.TextField(blank=True)
    experiments = models.ManyToManyField(Experiments, blank=True)
    frequency = models.ManyToManyField(Frequency, blank=True)
    keywords = models.ManyToManyField(Keywords, blank=True)
    model = models.ManyToManyField(Models, blank=True)
    variables = models.ManyToManyField(Variables, blank=True)
    def __str__(self):
        return self.title

