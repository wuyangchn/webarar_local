[简体中文](Deployment_zh_CN.md)

# Installation

The following instruction is for local usage. If you are planning to run WebArAr 
on a server computer instead, you can do much the same as mentioned below, but 
with some additional steps for a more stable application, such as replacing the 
built-in web server.

For Windows system:

#### 1. Install Python3

Following instructions on https://www.python.org/downloads/.

#### 2. Install and configure MySql

Following instructions on https://dev.mysql.com/doc/refman/8.3/en/windows-choosing-package.html

Remember the MySql server port (default 3306) and root password.

Create WebArAr databases: start MySql command line client -> using the command 
following to create database.

    create database webarar;
    # webarar can be other name as you want
    # Note that each MySql command ends with a semicolon
    
    # basic commands for reference:
    show databases;

#### 3. Redis

Redis on Windows https://github.com/microsoftarchive/redis

#### 4. Download source code

    # open CMD and cd to your location, clone webarar repository
    git clone https://github.com/wuyangchn/webarar.git
    
#### 5. Install requirements

    pip install -r requirements 
    
#### 6. Change settings.py

    # in settings.py, find and replace
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'webarar',  # MySql database name
            'HOST': '127.0.0.1',
            'PORT': 3306,  # port
            'USER': 'root',
            'PASSWORD': 'password'  # your password
        }
    }

#### 7. Run server

    python manage.py runserver

### 
