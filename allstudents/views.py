# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import UserProfile
from .serializers import StudentProfileSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Prefetch
from rest_framework.pagination import PageNumberPagination
from users.utils import api_response


class StudentPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'size'
    page_query_param = 'page'
    max_page_size = 100

class AllStudentsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StudentPagination

    def post(self, request):
        try:
            # Filters
            department = request.data.get('department')
            semester = request.data.get('semester')
            search = request.data.get('search')
            page = int(request.data.get('page', 1))
            size = int(request.data.get('size', 10))

            queryset = UserProfile.objects.filter(role='student').select_related('user')
            if department:
                queryset = queryset.filter(department=department)
            if semester:
                queryset = queryset.filter(semester=semester)
            if search:
                queryset = queryset.filter(user__full_name__icontains=search)

            queryset = queryset.annotate(total_post=Count('user__posts', distinct=True))

            # Manual pagination (like newsfeed)
            total = queryset.count()
            start = (page - 1) * size
            end = start + size
            paginated = queryset[start:end]

            serializer = StudentProfileSerializer(paginated, many=True)
            data = serializer.data
            return api_response(True, 'Students fetched successfully!', data, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)