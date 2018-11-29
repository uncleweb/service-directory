FROM praekeltfoundation/django-bootstrap

RUN apt-get-install.sh gettext

ENV DJANGO_SETTINGS_MODULE=service_directory.settings.docker

CMD ["service_directory.wsgi:application", "--timeout", "1800"]