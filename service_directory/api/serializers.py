from rest_framework import serializers
from models import Organisation, Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        depth = 1
