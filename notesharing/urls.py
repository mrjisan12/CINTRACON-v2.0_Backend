from django.urls import path 
from .views import *

urlpatterns = [
    path('create', NoteCreateView.as_view(), name="note_create"),
    path('all-notes', NoteListView.as_view(), name="all_notes"),
     path('detail/<int:note_id>', NoteDetailView.as_view(), name="note_detail"),
    path('update/<int:note_id>', NoteUpdateView.as_view(), name="note_update"),
    path('delete/<int:note_id>', NoteDeleteView.as_view(), name="note_delete"),
    path('increase-download/<int:note_id>', IncreaseDownloadCountView.as_view(), name="increase_download"),
]
