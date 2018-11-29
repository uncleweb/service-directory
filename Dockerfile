FROM praekeltfoundation/django-bootstrap

ENV DJANGO_SETTINGS_MODULE service_directory.project.docker

CMD ["service_directory.wsgi:application", "--timeout", "1800"]
