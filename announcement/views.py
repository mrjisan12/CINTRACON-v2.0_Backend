from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from .models import Announcement
from .serializers import AnnouncementSerializer, AnnouncementDetailSerializer
from users.utils import api_response
from users.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated


class CreateAnnouncementAPIView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            serializer = AnnouncementSerializer(data=request.data.copy())
            if serializer.is_valid():
                announcement = serializer.save(created_by=request.user)
                return api_response(True, 'Announcement created successfully!', AnnouncementSerializer(announcement).data, 201, status.HTTP_201_CREATED)
            return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateAnnouncementAPIView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id):
        try:
            try:
                announcement = Announcement.objects.get(id=id)
            except Announcement.DoesNotExist:
                return api_response(False, 'Announcement not found', None, 404, status.HTTP_404_NOT_FOUND)
            serializer = AnnouncementSerializer(announcement, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return api_response(True, 'Announcement updated successfully!', serializer.data, 200, status.HTTP_200_OK)
            return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteAnnouncementAPIView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id):
        try:
            try:
                announcement = Announcement.objects.get(id=id)
            except Announcement.DoesNotExist:
                return api_response(False, 'Announcement not found', None, 404, status.HTTP_404_NOT_FOUND)
            announcement.delete()
            return api_response(True, 'Announcement deleted successfully!', None, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllAnnouncementsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            page = int(request.data.get('page', 1))
            size = int(request.data.get('size', 10))
            search = request.data.get('search', '')

            queryset = Announcement.objects.select_related('created_by').all()
            if search:
                queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

            total = queryset.count()
            start = (page - 1) * size
            end = start + size
            serializer = AnnouncementSerializer(queryset[start:end], many=True)

            return api_response(True, 'Announcements fetched successfully!', serializer.data, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnnouncementDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            try:
                announcement = Announcement.objects.select_related('created_by').get(id=id)
            except Announcement.DoesNotExist:
                return api_response(False, 'Announcement not found', None, 404, status.HTTP_404_NOT_FOUND)
            return api_response(True, 'Announcement details fetched successfully!', AnnouncementDetailSerializer(announcement).data, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)
