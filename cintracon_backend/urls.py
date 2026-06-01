"""
URL configuration for cintracon_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from notesharing.views import PublicNoteDetailView
from jobopportunities.views import PublicJobDetailView
from upcomingevents.views import PublicEventDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('api/auth/', include('users.urls')),
    path('api/home/', include('home.urls')),
    path('api/all-students/', include('allstudents.urls')),
    path('api/job-opportunities/', include('jobopportunities.urls')),
    path('api/note-sharing/', include('notesharing.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/announcement/', include('announcement.urls')),
    path('api/events/', include('upcomingevents.urls')),
    path('api/maintenance/', include('maintenance.urls')),
    path('api/admin/', include('admin_panel.urls')),
    path('api/notifications/', include('notifications.urls')),

    # Public detail endpoints (no auth — for share links)
    path('api/notes/public/<int:note_id>/', PublicNoteDetailView.as_view(), name='note_public_detail'),
    path('api/jobs/public/<int:job_id>/', PublicJobDetailView.as_view(), name='job_public_detail'),
    path('api/events/public/<int:event_id>/', PublicEventDetailView.as_view(), name='event_public_detail'),

    # Social share OG meta pages (crawled by Facebook/WhatsApp/Twitter)
    path('share/post/<int:post_id>/', views.share_post_meta, name='share_post_meta'),
    path('share/note/<int:note_id>/', views.share_note_meta, name='share_note_meta'),
    path('share/job/<int:job_id>/', views.share_job_meta, name='share_job_meta'),
    path('share/event/<int:event_id>/', views.share_event_meta, name='share_event_meta'),
]
