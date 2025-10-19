from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Note
from .serializers import NoteSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .utils import api_response
from django.shortcuts import get_object_or_404


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
            search = request.data.get('search', '')  # Default to empty string

            notes = Note.objects.all().order_by('-uploaded_at')
            
            # Apply department filter
            if department:
                notes = notes.filter(department=department)
            
            # Apply semester filter  
            if semester:
                notes = notes.filter(semester=semester)
            
            # Apply search filter - search in title, description, course_code, and course_name
            if search:
                notes = notes.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search)
                )

            total = notes.count()
            start = (page - 1) * size
            end = start + size
            
            # Check if page exists
            if start >= total:
                return api_response(True, 'No more notes available', [], 200, status.HTTP_200_OK)
            
            paginated = notes[start:end]
            serializer = NoteSerializer(paginated, many=True)
            data = serializer.data
            
            
            return api_response(True, 'Notes fetched successfully!', data, 200, status.HTTP_200_OK)
            
        except ValueError:
            return api_response(False, 'Invalid page or size parameter', None, 400, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)




class NoteDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, note_id):
        try:
            # Get the note or return 404
            note = get_object_or_404(Note, id=note_id)
            
            # Serialize the note data
            serializer = NoteSerializer(note)
            
            return api_response(True, 'Note details fetched successfully!', serializer.data, 200, status.HTTP_200_OK)
            
        except Note.DoesNotExist:
            return api_response(False, 'Note not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class NoteUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, note_id):
        try:
            note = get_object_or_404(Note, id=note_id)
            
            # Check if the current user is the owner of the note
            if note.user != request.user:
                return api_response(False, 'You can only update your own notes', None, 403, status.HTTP_403_FORBIDDEN)
            
            serializer = NoteSerializer(note, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return api_response(True, 'Note updated successfully!', serializer.data, 200, status.HTTP_200_OK)
            
            return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)
            
        except Note.DoesNotExist:
            return api_response(False, 'Note not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class NoteDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, note_id):
        try:
            note = get_object_or_404(Note, id=note_id)
            
            # Check if the current user is the owner of the note
            if note.user != request.user:
                return api_response(False, 'You can only delete your own notes', None, 403, status.HTTP_403_FORBIDDEN)
            
            note.delete()
            return api_response(True, 'Note deleted successfully!', None, 200, status.HTTP_200_OK)
            
        except Note.DoesNotExist:
            return api_response(False, 'Note not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
        
 # Download count increase API view       
class IncreaseDownloadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, note_id):
        try:
            note = get_object_or_404(Note, id=note_id)
            
            # Increase download count
            note.total_downloads += 1
            note.save()
            
            return api_response(
                True, 
                'Download count increased successfully!', 
                {'total_downloads': note.total_downloads}, 
                200, 
                status.HTTP_200_OK
            )
            
        except Note.DoesNotExist:
            return api_response(False, 'Note not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)