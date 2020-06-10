******************
Getting Started
******************


About
=====

Publication Hub is a publication management site for group and organizations that produce more publications than can be managed by hand.

-------

Installation
============

.. note::
    You will need to following software installed to follow these instructions:
        * `Python 3 <https://www.python.org/download/>`_
        * `Virtualenv <https://virtualenv.pypa.io/en/latest/installation/>`_
        * `Git <https://git-scm.com/downloads>`_

Begin by downloading the project files with git:

.. code-block:: bash

    git clone https://github.com/aims-group/publication-site.git

From inside the new folder, execute the following commands:

.. code-block:: bash

    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
    cp local_settings_example.py local_settings.py

Before continuing, open the local_settings and set each variable to a valid setting.

Next run the following commands:

.. code-block:: bash

    python manage.py makemigrations
    python manage.py makemigrations publisher
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py collectstatic

-------

Configuration
=============================

Now that the databse has the proper tables, the following files should be edited and customized based on your own use cases.

 * scripts/experiment.py
 * scripts/frequency.py
 * scripts/keyword.py
 * scripts/model.py
 * scripts/variable.py
 * scripts/journals.py

The files are used to populate the database with relevant meta data. The meta data is currently designed with climate science in mind, but these files can be customized to fit a variety of needs. Each of the files generally follows a pattern of declaring a project, then a list of relevant tags. For example, the CMIP5 project has various climate models, so each model is listed in the model.py file which allows users to optionally tag a publication as being related to that model. 
The exception to this pattern is the journals.py file. Journals often have long names, and there are various abbreviations for any given journal. The **full names** of journals relevant to the publications to be stored should be placed here.

Each of the files (except journals.py) represents a category of metadata that will be shown to users as possible tags for a given project. For instance:

.. code-block:: python

    keyword_data = [
    {'project_name': 'my-project',
     'keywords': [
         'keyword1',
         'keyword2'
     ]},
    {'project_name': 'another-project',
     'keywords': [
         'keyword1',
         'keyword2',
         'keyword3',
     ]},
    ]

When a user selects 'my-project' for a publication they will be given the option to tag it with the keywords "keyword1", and "keyword2". Duplicate tags such as "keyword1" and "keywrod2" are fully supported.

Once these files are filled in run the following commands:

.. code-block:: bash

    python manage.py initialize

Development Settings
---------------------

Inside the local_settings.py file there are various keys and settings that need to be set for full functionality.

You can generate the secret key with the following python lines: 

.. code-block:: python

    import random
    ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))


.. code-block: python

    EMAIL_HOST = 'localhost' 
    EMAIL_PORT = 1025       # We will run a development server that will listen to this port

Finally, make sure to set the google captcha keys. https://www.google.com/recaptcha/intro/ will explain how to get them. 


With those settings added, we just need a local smtp server to for debugging password reset emails. 
Run this command in a separate terminal. (Any emails sent will appear as plain text in this window.)

.. code-block:: bash

    python -m smtpd -n -c DebuggingServer localhost:1025

Now you can run the server locally:

.. code-block:: bash

    python manage.py runserver

Load Production Data For Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In some cases, it can be very useful to have real world data to test with. The generalized steps for setting this up are as follows:

* Install Postgress (If you are on Mac, you can use postgresapp.com)

* Create a new database (optional for mac. postgressapp creates a database with your username)

* Update your local_settings.py file to connect to the new database

* Dump the remote database to a file and load it into your local database. https://www.postgresql.org/docs/9.1/static/backup-dump.html


Production Settings
---------------------

**Production** versions should set the full suite of smtp options according to the mail server being used.
Sometimes this may only require setting the ``EMAIL_HOST`` field, while other servers may require more settings. 

In a **Production** environment, apache/mod_wsgi will be responsible for serving the site.