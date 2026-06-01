from django.urls import path 
from .views import *

urlpatterns = [
    path('create', EventCreateView.as_view(), name="event_create"),
    path('all-events', EventListView.as_view(), name="all_events"),
    path('update/<int:event_id>', EventUpdateView.as_view(), name="event_update"),
    path('delete/<int:event_id>', EventDeleteView.as_view(), name="event_delete"),
    path('interest/<int:event_id>', EventInterestView.as_view(), name="event_interest"),
    path('my-interests', UserInterestedEventsView.as_view(), name="user_interested_events"),
]