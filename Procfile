web: daphne HackerDistro.wsgi:application --port $PORT --bind 0.0.0.0 -v2
SiteWorker: python manage.py runworker --settings=HackerDistro.settings -v2
Celeryworker: celery -A HackerDistro worker -b -l info