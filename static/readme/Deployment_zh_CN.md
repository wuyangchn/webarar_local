[English](Deployment.md)


# 部署

以下说明仅供本地部署使用。如果你打算在服务器上运行 WebArAr，你可以做下面提到的相同的事情，
但是需要一些额外的步骤来获得一个更稳定的应用程序，比如替换性能更强大的 web 服务器。

For Windows system:

#### 1. 安装 Python3

Following instructions on https://www.python.org/downloads/.

#### 2. Install and configure MySql

Following instructions on https://dev.mysql.com/doc/refman/8.3/en/windows-choosing-package.html

Remember the MySql server port (default 3306) and root password.

Create WebArAr databases: start MySql command line client -> using the command following to create database.

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
