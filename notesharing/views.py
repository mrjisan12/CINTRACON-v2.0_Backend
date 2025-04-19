from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Note
from .serializers import NoteSerializer

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
        serializer = NoteSerializer(notes, many=True)
        return Response({
            'msg': 'Notes fetched successfully!',
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
