# **_HackerDistro_**

---

## **Reference**
- Hacker News


---

## **Project Description**

Hacker Distro is a simple web app that consumes HackerNews api and displays the data to users on its frontend 
It also exposes a simple REST api to perform crud Operations

---

## Dependenciies
    1. python
    2. Django
    3. Django Rest Framework
    4. Redis
    6. Celery
    7. Docker

## **Runing Project Locally**
    In your terminal change directory to the project's root folder the run: 
        `docker-compose build django`
    
        `docker-compose run django  python manage.py makemigrations`
        `docker-compose run django  python manage.py migrate`

        `docker-compose up`


## Check Live Demo at:
    https://hackerdistro.herokuapp.com/
    
    API :
        https://hackerdistro.herokuapp.com/swagger/
        https://hackerdistro.herokuapp.com/redoc/
