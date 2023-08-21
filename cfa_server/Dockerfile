FROM python:3.11.3-slim-bullseye

# ENV PYTHONPATH="$PYTHONPATH:/home/grepsr/$SERVICE_NAME/src"
ADD requirements.txt /tmp/requirements.txt
# gis dependencies
RUN apt-get update \
    && apt-get install -y libspatialite-dev gdal-bin libgdal-dev proj-bin python3-gdal libsqlite3-mod-spatialite \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install psycopg2-binary \
    && rm -rf /var/lib/apt/lists/*

# Make a dir inside
RUN mkdir -p /cfa_server
    
ADD . /cfa_server

WORKDIR /cfa_server/

# RUN python manage.py collectstatic --noinput

CMD gunicorn cfa_server.wsgi:application -c gunicorn_config.py
