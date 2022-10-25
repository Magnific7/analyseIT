# django-template

This is a sample django project

## Clone Project

HTTPS: git remote add origin https://github.com/Magnific7/django-template.git

SSH: git remote add origin git@github.com:Magnific7/django-template.git

### Create a virtual environment

install virstualenv >>>> pip install virtualenv
create venv >>>> virtualenv venv
Activate >>> source venv/bin/activate (linux)
Activate >>> source venv/Scripts/activate (windows)

#### Add .env file

create a file called .env
Add credentials to the db with the format in the .env_example

### Migrations

Delete migrations file
make migrations >>>> python manage.py makemigrations analyseIT_app
migrate >>>> python manage.py migrate

#### Create a superuser

winpty python manage.py createsuperuser

#### Run the project

Python manage.py runserver

#### Browser access

http://127.0.0.1:8000/analyseIT_app/
