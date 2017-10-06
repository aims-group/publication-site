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
        * `Python 2.7 <https://www.python.org/download/releases/2.7/>`_
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
    python manage.py runserver

For **development**, use the following line to start a simple smtp server:

.. code-block:: bash

    python -m smtpd -n -c DebuggingServer localhost:1025

Inside of local_settings.py you will want to set the following values:

.. code-block:: bash

    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025

**Production** versions should set the full suite of smtp options according to the mail server being used.
