FROM praekeltfoundation/django-bootstrap:py2.7

ENV DJANGO_SETTINGS_MODULE service_directory.project.docker

COPY . /app
RUN pip install -e .

CMD ["service_directory.wsgi:application", "--timeout", "1800"]
