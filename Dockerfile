# https://github.com/tiangolo/uwsgi-nginx-flask-docker

FROM tiangolo/uwsgi-nginx-flask:python3.10

COPY ./slackapp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./slackapp /app
