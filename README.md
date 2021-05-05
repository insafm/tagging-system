* PipEnv is a way to create virtual environments in Python that allows for environment agnostic dependency installation.


Tagging System
--------------------------------------------------------


Installation Steps:
-----------------------------
- git clone URL

- cd tagging-system

- python3 -m pip3 install pipenv

- python3 -m pipenv install -r requirements.txt --skip-lock

- python3 -m pipenv shell

- service postgresql start
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
DATABASE NAME: instest_post
USER: postgres
PASSWORD: postgres
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- python3 manage.py migrate

- python3 manage.py createsuperuser

- python3 manage.py runserver 0:7777

- Goto http://127.0.0.1:7777 and login.

INFO: Don't hesitate to contact me if any issue occured while installation. Mail: me@insafweb.in