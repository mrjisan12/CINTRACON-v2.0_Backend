from django.urls import path
from .views import *

urlpatterns = [
    path('status', MaintenanceStatusAPIView.as_view(), name='maintenance-status'),
    path('update-status', UpdateMaintenanceStatusAPIView.as_view(), name='update-maintenance-status'),
    path('create-status', CreateMaintenanceStatusAPIView.as_view(), name='create-maintenance-status'),  # New API
]