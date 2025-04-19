from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import JobPostSerializer
from rest_framework.permissions import IsAuthenticated
from .models import *

class JobPostCreateView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can create job posts

    def post(self, request):
        # Add the user from the request to the data before saving
        serializer = JobPostSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user explicitly
            return Response({
                'msg': 'Job post successfully created!',
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class JobPostListView(APIView):
    def get(self, request):
        # Get all job posts (you can add pagination here for large datasets)
        job_posts = JobPost.objects.all().order_by('-created_at')
        serializer = JobPostSerializer(job_posts, many=True)
        return Response({
            'msg': 'Job posts fetched successfully!',
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
        
        
