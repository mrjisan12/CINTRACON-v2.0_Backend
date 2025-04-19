from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Note
from .serializers import NoteSerializer
from rest_framework.pagination import PageNumberPagination


class NoteSharingPostPagination(PageNumberPagination):
    page_size = 10  # Adjust to the number of posts you want per request



class NoteCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NoteSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'msg': 'Note uploaded successfully!',
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NoteListView(APIView):
    def get(self, request):
        notes = Note.objects.all().order_by('-uploaded_at')
        # Paginate the queryset
        paginator = NoteSharingPostPagination()
        result_page = paginator.paginate_queryset(notes, request)
        
        serializer = NoteSerializer(result_page, many=True)
        return paginator.get_paginated_response(
            {
                'msg': 'Notes fetched successfully!',
                'success': True,
                'data': serializer.data,
                'code': 200
            }
        )


