# DRF-Boilerplate
This is a django rest framework project boilerplate.
This project is running on django version 5.0.7 and python version 3.12.3


# Introduction
The goal of this project is to learn django rest framework professional and everyone can use this project.

_Also want to cover up this things_
* Serialization
* Request & Response
* Class based views
* Authentication & permission
* Relationships & hyperlinked APIs
* Viewsets & router


# Project Setup

To use this project to your own machine follow this steps

### Clone repository from github

First of all, clone this repository using this command

    git clone https://github.com/mehedishovon01/drf-boilerplate.git

### Create a virtualenv

Make a virtual environment to your project directory. Let's do this,

If you have already an existing python virtualenv then run this

    virtualenv venv

Or if virtualenv is not install in you machine then run this

    python -m venv venv
    
Activate the virtual environment and verify it

    . venv/bin/activate

### Install the dependencies

Most of the projects have dependency name like requirements.txt file which specifies the requirements of that project, so let’s install the requirements of it from the file.

    pip install -r requirements.txt

### The project layouts

```
DRF-Boilerplate
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── .gitignore
├── LICENSE
├── manage.py
├── README.md
└── requirements.txt
```

### Make an .env

Copy .env from .env.example file for put the secret credentials

    cp .env.example .env

After that, put the database credentials and mail credentials `(Do not use the direct Mail Password)`


### Create database

We have already configured the MySQL in our project.

So, simply apply the migrations:

    python manage.py migrate
    
Boooooom! Project setup is done.

### Run this project

Let's run the development server:

    python manage.py runserver

That’s it! Now you’re project is already run into a development server. 

Just click this link, [http://127.0.0.1:8000/](http://127.0.0.1:8000/)


Thanks for reading.# Ankand-Auction
