from django.urls import path
from . import views

urlpatterns = [
    path('create', views.CreateAnnouncementAPIView.as_view(), name='create-announcement'),
    path('update/<int:id>', views.UpdateAnnouncementAPIView.as_view(), name='update-announcement'),
    path('delete/<int:id>', views.DeleteAnnouncementAPIView.as_view(), name='delete-announcement'),
    path('all', views.AllAnnouncementsAPIView.as_view(), name='all-announcements'),
    path('detail/<int:id>', views.AnnouncementDetailAPIView.as_view(), name='announcement-detail'),
]
