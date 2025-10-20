from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Announcement
from .serializers import AnnouncementSerializer, AnnouncementDetailSerializer
from users.utils import api_response

class CreateAnnouncementAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data.copy()
            
            serializer = AnnouncementSerializer(data=data)
            if serializer.is_valid():
                # Save with the user as created_by
                announcement = serializer.save(created_by=request.user)
                
                # Now serialize the saved instance to return
                response_serializer = AnnouncementSerializer(announcement)
                
                return api_response(
                    True, 
                    'Announcement created successfully!', 
                    response_serializer.data, 
                    201, 
                    status.HTTP_201_CREATED
                )
            else:
                return api_response(
                    False, 
                    'Validation error', 
                    serializer.errors, 
                    400, 
                    status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return api_response(
                False, 
                f'Server error: {str(e)}', 
                None, 
                500, 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AllAnnouncementsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            page = int(request.data.get('page', 1))
            size = int(request.data.get('size', 10))
            search = request.data.get('search', '')
            
            # Build queryset
            queryset = Announcement.objects.select_related('created_by').all()
            
            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search)
                )
            
            # Manual pagination (your existing pattern)
            total = queryset.count()
            start = (page - 1) * size
            end = start + size
            
            # Get paginated data
            announcements = queryset[start:end]
            
            serializer = AnnouncementSerializer(announcements, many=True)
            
            # Prepare response data with pagination info
            response_data = serializer.data
            
            return api_response(
                True, 
                'Announcements fetched successfully!', 
                response_data, 
                200, 
                status.HTTP_200_OK
            )
            
        except Exception as e:
            return api_response(
                False, 
                f'Server error: {str(e)}', 
                None, 
                500, 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AnnouncementDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        try:
            try:
                announcement = Announcement.objects.select_related('created_by').get(id=id)
            except Announcement.DoesNotExist:
                return api_response(
                    False, 
                    'Announcement not found', 
                    None, 
                    404, 
                    status.HTTP_404_NOT_FOUND
                )
            
            serializer = AnnouncementDetailSerializer(announcement)
            
            return api_response(
                True, 
                'Announcement details fetched successfully!', 
                serializer.data, 
                200, 
                status.HTTP_200_OK
            )
            
        except Exception as e:
            return api_response(
                False, 
                f'Server error: {str(e)}', 
                None, 
                500, 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )