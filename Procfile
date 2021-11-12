web: daphne HackerDistro.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: celery -A HackerDistro worker -b -l info

