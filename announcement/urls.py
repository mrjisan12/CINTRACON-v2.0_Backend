from django.urls import path
from . import views

urlpatterns = [
    path('create', views.CreateAnnouncementAPIView.as_view(), name='create-announcement'),
    path('all', views.AllAnnouncementsAPIView.as_view(), name='all-announcements'),
    path('detail/<int:id>', views.AnnouncementDetailAPIView.as_view(), name='announcement-detail'),
]