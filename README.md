# publication-site

A Django skeleton site for tracking publications, posters, presentations...

    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py makemigrations publisher
    python manage.py migrate
    python manage.py migrate publisher
    python manage.py createsuperuser
     > username:
     > email:
     > password:
     > password:
    python manage.py initialize
    python manage.py runserver

The **initialize** command reads from the following files inside the "scripts" folder:

    experiment.py
    frequency.py
    journals.py
    keyword.py
    model.py
    variable.py

The files are used to populate the database with relevant meta data. The meta data is currently designed with climate science in mind,
but these files can be customized to fit a variety of needs. Each of the files generally follows a pattern of declaring a project,
then a list of relevant tags. For example, the CMIP5 project has various climate models, so each model is listed in the model.py file which allows users to optionally
tag a publication as being related to that model. 

The exception to this pattern is the journals.py file. Journals often have long names, and there are various abbreviations for any given journal. 
The **full names** of journals relevant to the publications to be stored should be placed here.


For development use the following line to start a simple smtp server:

    python -m smtpd -n -c DebuggingServer localhost:1025

Inside of local_settings.py you will want to set the following values:

    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    RECAPTCHA_PUBLIC_KEY = "your_recaptcha_site_key"
    RECAPTCHA_PRIVATE_KEY = "your_recaptcha_private_key"

Production versions should set the full suite of smtp options according to the mail server being used.
    
The recaptcha keys can be obtained from https://www.google.com/recaptcha/intro/

Google may require a domain to be listed when defining the key settings. For production, this will simply be the sites own domain,
but for development, localhost works just fine.
