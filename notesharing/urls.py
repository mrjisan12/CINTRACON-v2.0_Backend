from django.urls import path 
from .views import *

urlpatterns = [
    path('create/', NoteCreateView.as_view(), name="note_create"),
    path('all-notes/', NoteListView.as_view(), name="all_notes"),
]
