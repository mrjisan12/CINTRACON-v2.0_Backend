from django.urls import path 
from .views import *

urlpatterns = [
    path('create', JobPostCreateView.as_view(), name="job_create"),
    path('all-jobs', JobPostListView.as_view(), name="all_jobs"),
     path('delete/<int:job_id>', JobPostDeleteView.as_view(), name="job_delete"),
]
