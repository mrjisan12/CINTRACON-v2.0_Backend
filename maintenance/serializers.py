from .models import *
from rest_framework import serializers


class MaintenanceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceStatus
        fields = ['status', 'reason', 'created_at']