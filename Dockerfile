FROM python:3.8-alpine
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install -r requirements.txt

