from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from users.permissions import IsAdmin
from users.utils import api_response
from users.models import CustomUser, UserProfile
from home.models import Post, Report
from notesharing.models import Note
from jobopportunities.models import JobPost
from upcomingevents.models import Event
from announcement.models import Announcement
from .models import SiteSettings


class AdminDashboardStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            seven_days_ago = timezone.now() - timedelta(days=7)
            data = {
                'total_students': UserProfile.objects.filter(role='student').count(),
                'total_posts': Post.objects.count(),
                'total_notes': Note.objects.count(),
                'total_jobs': JobPost.objects.count(),
                'total_events': Event.objects.count(),
                'total_announcements': Announcement.objects.count(),
                'total_forum_topics': Post.objects.count(),
                'recent_signups': CustomUser.objects.filter(date_joined__gte=seven_days_ago).count(),
                'recent_posts': Post.objects.filter(created_at__gte=seven_days_ago).count(),
                'reported_posts_pending': Report.objects.filter(status='pending').count(),
            }
            return api_response(True, 'Dashboard stats fetched successfully!', data, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Students ────────────────────────────────────────────────────────────────

class AdminStudentListView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            search = request.data.get('search', '')
            department = request.data.get('department', '')
            semester = request.data.get('semester', '')
            page = int(request.data.get('page', 1))
            size = int(request.data.get('size', 10))

            profiles = UserProfile.objects.select_related('user').filter(role='student')
            if search:
                profiles = profiles.filter(
                    Q(user__full_name__icontains=search) | Q(user__email__icontains=search)
                )
            if department:
                profiles = profiles.filter(department=department)
            if semester:
                profiles = profiles.filter(semester=semester)

            total = profiles.count()
            start = (page - 1) * size
            end = start + size
            paginated = profiles[start:end]

            data = [
                {
                    'id': p.user.id,
                    'name': p.user.full_name,
                    'email': p.user.email,
                    'department': p.department,
                    'semester': p.semester,
                    'batch': p.batch_no,
                    'profile_photo': p.profile_photo.url if p.profile_photo else None,
                    'is_active': p.user.is_active,
                    'date_joined': p.user.date_joined,
                }
                for p in paginated
            ]
            return api_response(True, 'Students fetched successfully!', data, 200, status.HTTP_200_OK, pagination={
                'total': total, 'page': page, 'size': size,
                'total_pages': (total + size - 1) // size if size else 1
            })
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminStudentDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, student_id):
        try:
            user = CustomUser.objects.get(id=student_id)
            user.delete()
            return api_response(True, 'Student deleted', None, 200, status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return api_response(False, 'Student not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminStudentToggleActiveView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, student_id):
        try:
            user = CustomUser.objects.get(id=student_id)
            user.is_active = not user.is_active
            user.save()
            return api_response(True, 'Student status updated', {'is_active': user.is_active}, 200, status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return api_response(False, 'Student not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Forum (Posts) ────────────────────────────────────────────────────────────

class AdminForumListView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            search = request.data.get('search', '')
            page = int(request.data.get('page', 1))
            size = int(request.data.get('size', 10))

            posts = Post.objects.select_related('user').prefetch_related('comments').all()
            if search:
                posts = posts.filter(Q(caption__icontains=search))

            total = posts.count()
            start = (page - 1) * size
            end = start + size
            paginated = posts[start:end]

            data = [
                {
                    'id': p.id,
                    'title': p.caption[:120] if p.caption else '',
                    'author': p.user.full_name,
                    'created_at': p.created_at,
                    'replies_count': p.comments.count(),
                    'is_pinned': p.is_pinned,
                    'is_active': True,
                }
                for p in paginated
            ]
            return api_response(True, 'Forum topics fetched successfully!', data, 200, status.HTTP_200_OK, pagination={
                'total': total, 'page': page, 'size': size,
                'total_pages': (total + size - 1) // size if size else 1
            })
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminForumDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, topic_id):
        try:
            post = Post.objects.get(id=topic_id)
            post.delete()
            return api_response(True, 'Topic deleted', None, 200, status.HTTP_200_OK)
        except Post.DoesNotExist:
            return api_response(False, 'Topic not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminForumPinView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, topic_id):
        try:
            post = Post.objects.get(id=topic_id)
            post.is_pinned = not post.is_pinned
            post.save()
            msg = 'Topic pinned' if post.is_pinned else 'Topic unpinned'
            return api_response(True, msg, {'is_pinned': post.is_pinned}, 200, status.HTTP_200_OK)
        except Post.DoesNotExist:
            return api_response(False, 'Topic not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Notes ───────────────────────────────────────────────────────────────────

class AdminNoteListView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            search = request.data.get('search', '')
            department = request.data.get('department', '')
            page = int(request.data.get('page', 1))
            size = int(request.data.get('size', 10))

            notes = Note.objects.select_related('user').all()
            if search:
                notes = notes.filter(Q(title__icontains=search) | Q(description__icontains=search))
            if department:
                notes = notes.filter(department=department)

            total = notes.count()
            start = (page - 1) * size
            end = start + size
            paginated = notes[start:end]

            data = [
                {
                    'id': n.id,
                    'title': n.title,
                    'subject': n.description[:80] if n.description else '',
                    'department': n.department,
                    'uploaded_by': n.user.full_name,
                    'created_at': n.uploaded_at,
                    'downloads': n.total_downloads,
                    'file': n.drive_link or (n.note_file.url if n.note_file else None),
                }
                for n in paginated
            ]
            return api_response(True, 'Notes fetched successfully!', data, 200, status.HTTP_200_OK, pagination={
                'total': total, 'page': page, 'size': size,
                'total_pages': (total + size - 1) // size if size else 1
            })
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminNoteDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, note_id):
        try:
            note = Note.objects.get(id=note_id)
            note.delete()
            return api_response(True, 'Note deleted', None, 200, status.HTTP_200_OK)
        except Note.DoesNotExist:
            return api_response(False, 'Note not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Reports ─────────────────────────────────────────────────────────────────

class AdminReportsListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            reports = Report.objects.select_related('user', 'post').filter(status='pending').order_by('-created_at')
            data = [
                {
                    'id': r.id,
                    'post_id': r.post.id,
                    'post_content': r.post.caption[:120] if r.post.caption else '',
                    'reported_by': r.user.full_name,
                    'reason': r.reason,
                    'status': r.status,
                    'created_at': r.created_at,
                }
                for r in reports
            ]
            return api_response(True, 'Reports fetched successfully!', data, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminReportResolveView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, report_id):
        try:
            report = Report.objects.select_related('post').get(id=report_id)
            action = request.data.get('action')
            if action == 'delete_post':
                report.post.delete()
            elif action == 'dismiss':
                report.status = 'dismissed'
                report.save()
            elif action == 'warn_user':
                report.status = 'resolved'
                report.save()
            else:
                return api_response(False, 'Invalid action. Use delete_post, dismiss, or warn_user.', None, 400, status.HTTP_400_BAD_REQUEST)
            return api_response(True, 'Report resolved', None, 200, status.HTTP_200_OK)
        except Report.DoesNotExist:
            return api_response(False, 'Report not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Settings ────────────────────────────────────────────────────────────────

class AdminSettingsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            from maintenance.models import MaintenanceStatus
            settings_obj, _ = SiteSettings.objects.get_or_create(id=1)
            maintenance = MaintenanceStatus.objects.last()
            data = {
                'site_name': settings_obj.site_name,
                'allow_signup': settings_obj.allow_signup,
                'max_file_size_mb': settings_obj.max_file_size_mb,
                'allowed_departments': settings_obj.allowed_departments,
                'maintenance_mode': maintenance.status if maintenance else False,
            }
            return api_response(True, 'Settings fetched successfully!', data, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminSettingsUpdateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            from maintenance.models import MaintenanceStatus
            settings_obj, _ = SiteSettings.objects.get_or_create(id=1)

            for field in ('site_name', 'allow_signup', 'max_file_size_mb', 'allowed_departments'):
                if field in request.data:
                    setattr(settings_obj, field, request.data[field])
            settings_obj.save()

            if 'maintenance_mode' in request.data:
                maintenance = MaintenanceStatus.objects.last()
                if maintenance:
                    maintenance.status = request.data['maintenance_mode']
                    maintenance.save()

            return api_response(True, 'Settings updated', None, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)
