FROM python:3.8-slim-buster

# ENV PYTHONPATH="$PYTHONPATH:/home/grepsr/$SERVICE_NAME/src"

# Make a dir inside
RUN mkdir -p /cfa_server  

ADD requirements.txt /tmp/requirements.txt

RUN apt-get -y update \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install psycopg2-binary 

ADD . /cfa_server

WORKDIR /cfa_server/

RUN python manage.py collectstatic -y

CMD python cfa_server/manage.py runserver 0.0.0.0:8001
