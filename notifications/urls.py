from django.urls import path
from .views import NotificationListView, NotificationMarkReadView, NotificationDeleteView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('mark-read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('<int:pk>/', NotificationDeleteView.as_view(), name='notification-delete'),
]
