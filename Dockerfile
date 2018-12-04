FROM praekeltfoundation/django-bootstrap:py2.7

ENV DJANGO_SETTINGS_MODULE service_directory.project.docker

# installing Geospatial libraries https://docs.djangoproject.com/en/1.8/ref/contrib/gis/install/geolibs/
RUN apt-get update && apt-get -y --force-yes install binutils libproj-dev gdal-bin

COPY . /app
RUN pip install -e .

CMD ["service_directory.project.wsgi:application", "--timeout", "1800"]
