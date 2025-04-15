from django.urls import path 
from . import views

urlpatterns = [
    path('', views.AllStudentsAPIView.as_view() , name="all_students")
]
