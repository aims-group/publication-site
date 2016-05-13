# cmip6-publication-site
new CMDIP6 Publication reporting site

    virtualenv2 env
    source env/bin/activate
    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py makemigrations publisher
    python manage.py migrate
    python mangae.py migrate publisher
    python manage.py createsuperuser
     > username:
     > email:
     > password:
     > password:
    python manage.py load_data
    python manage.py runserver

To prevent unnecessary server load, the network graph reads from a static json file.
Create and update the json file by running the following command:
    python manage.py createjson

It is recommended that this command be set up to run nightly (via a cron job for example).