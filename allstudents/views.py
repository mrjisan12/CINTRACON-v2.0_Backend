# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import UserProfile
from .serializers import StudentProfileSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Prefetch
from rest_framework.pagination import PageNumberPagination

# Without dept and semester filter and paginations

# class AllStudentsAPIView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         # Get all user profiles with role 'student'
#         student_profiles = UserProfile.objects.filter(role='student')
        
#         # Serialize the data
#         serializer = StudentProfileSerializer(student_profiles, many=True)
        
#         # Prepare the response structure
#         response_data = {
#             "msg": "All Student Profile Retrieved Successfully",
#             "success": True,
#             "data": serializer.data,
#             "code": status.HTTP_200_OK
#         }
        
#         return Response(response_data, status=status.HTTP_200_OK)




# New Optimized Code with dept and semester filter
# views.py (Optimized Query)

class StudentPagination(PageNumberPagination):
    page_size = 20  # Default page size
    page_size_query_param = 'page_size'
    max_page_size = 100

class AllStudentsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StudentPagination

    def post(self, request):
        department = request.data.get('department', 'cse')  # Default to CSE
        semester = request.data.get('semester')  # Optional filter
        
        # Base queryset with optimizations
        queryset = UserProfile.objects.filter(
            role='student',
            department=department
        ).select_related('user').only(
            'department', 'semester', 'batch_no', 
            'points', 'section', 'profile_photo',
            'user__first_name', 'user__last_name', 'user__email'
        )
        
        if semester:
            queryset = queryset.filter(semester=semester)
        
        # Annotate post count
        queryset = queryset.annotate(
            total_post=Count('user__posts', distinct=True)
        )
        
        # Paginate results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        serializer = StudentProfileSerializer(page, many=True)
        
        return paginator.get_paginated_response({
            "msg": f"All {department.upper()} Students Retrieved",
            "success": True,
            "data": serializer.data,
            "code": 200
        })