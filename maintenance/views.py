from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import MaintenanceStatusSerializer
from .utils import api_response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.

# Create Maintenance Status API
class CreateMaintenanceStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            status_flag = request.data.get('status')
            reason = request.data.get('reason', '')
            
            # Validate required fields
            if status_flag is None:
                return api_response(
                    success=False,
                    msg="Status field is required",
                    code=status.HTTP_400_BAD_REQUEST,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Create new maintenance status
            maintenance = MaintenanceStatus.objects.create(
                status=status_flag,
                reason=reason
            )
            
            serializer = MaintenanceStatusSerializer(maintenance)
            return api_response(
                success=True,
                msg="Maintenance status created successfully",
                data=serializer.data,
                code=status.HTTP_201_CREATED,
                status_code=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return api_response(
                success=False,
                msg=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Maintenance Status APIs
class MaintenanceStatusAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            # Get the latest maintenance status
            maintenance = MaintenanceStatus.objects.last()
            if not maintenance:
                # Create default entry if none exists
                maintenance = MaintenanceStatus.objects.create(status=False, reason="")
            
            serializer = MaintenanceStatusSerializer(maintenance)
            return api_response(
                success=True,
                msg="Maintenance status retrieved successfully",
                data=serializer.data,
                code=status.HTTP_200_OK,
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            return api_response(
                success=False,
                msg=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateMaintenanceStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            status_flag = request.data.get('status', False)
            reason = request.data.get('reason', '')
            
            maintenance = MaintenanceStatus.objects.last()
            if not maintenance:
                maintenance = MaintenanceStatus.objects.create(status=status_flag, reason=reason)
            else:
                maintenance.status = status_flag
                maintenance.reason = reason
                maintenance.save()
            
            serializer = MaintenanceStatusSerializer(maintenance)
            return api_response(
                success=True,
                msg=f'Maintenance status updated to {status_flag}',
                data=serializer.data,
                code=status.HTTP_200_OK,
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            return api_response(
                success=False,
                msg=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )