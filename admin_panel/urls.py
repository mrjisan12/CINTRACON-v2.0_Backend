from django.urls import path
from . import views

urlpatterns = [
    path('dashboard-stats/', views.AdminDashboardStatsView.as_view(), name='admin-dashboard-stats'),

    # Students
    path('students/', views.AdminStudentListView.as_view(), name='admin-students'),
    path('students/<int:student_id>/', views.AdminStudentDeleteView.as_view(), name='admin-student-delete'),
    path('students/<int:student_id>/toggle-active/', views.AdminStudentToggleActiveView.as_view(), name='admin-student-toggle'),

    # Forum (Posts)
    path('forum/', views.AdminForumListView.as_view(), name='admin-forum'),
    path('forum/<int:topic_id>/', views.AdminForumDeleteView.as_view(), name='admin-forum-delete'),
    path('forum/<int:topic_id>/pin/', views.AdminForumPinView.as_view(), name='admin-forum-pin'),

    # Notes
    path('notes/', views.AdminNoteListView.as_view(), name='admin-notes'),
    path('notes/<int:note_id>/', views.AdminNoteDeleteView.as_view(), name='admin-note-delete'),

    # Reports
    path('reports/', views.AdminReportsListView.as_view(), name='admin-reports'),
    path('reports/<int:report_id>/resolve/', views.AdminReportResolveView.as_view(), name='admin-report-resolve'),

    # Settings
    path('settings/', views.AdminSettingsView.as_view(), name='admin-settings'),
    path('settings/update/', views.AdminSettingsUpdateView.as_view(), name='admin-settings-update'),
]
