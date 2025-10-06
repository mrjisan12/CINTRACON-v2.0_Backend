from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Note
from .serializers import NoteSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q


class NoteSharingPostPagination(PageNumberPagination):
    page_size = 10  # Adjust to the number of posts you want per request



class NoteCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .utils import api_response
        try:
            serializer = NoteSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return api_response(True, 'Note uploaded successfully!', serializer.data, 201, status.HTTP_201_CREATED)
            return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class NoteListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .utils import api_response
        try:
            page = int(request.data.get('page', 1))
            size = int(request.data.get('size', 10))
            department = request.data.get('department')
            semester = request.data.get('semester')
            search = request.data.get('search')

            notes = Note.objects.all().order_by('-uploaded_at')
            if department:
                notes = notes.filter(department=department)
            if semester:
                notes = notes.filter(semester=semester)
            if search:
                notes = notes.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search)
                )

            total = notes.count()
            start = (page - 1) * size
            end = start + size
            paginated = notes[start:end]
            serializer = NoteSerializer(paginated, many=True)
            data = {
                'results': serializer.data,
                'total': total,
                'page': page,
                'size': size
            }
            return api_response(True, 'Notes fetched successfully!', data, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


