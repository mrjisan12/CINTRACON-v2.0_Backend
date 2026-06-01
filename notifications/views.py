from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from users.utils import api_response


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            page = int(request.query_params.get('page', 1))
            size = int(request.query_params.get('size', 20))

            qs = request.user.notifications.select_related('sender').all()
            unread_count = qs.filter(is_read=False).count()
            total = qs.count()
            start = (page - 1) * size
            paginated = qs[start:start + size]

            data = [
                {
                    'id': n.id,
                    'type': n.notif_type,
                    'message': n.message,
                    'link': n.link,
                    'is_read': n.is_read,
                    'created_at': n.created_at,
                    'sender_name': n.sender.full_name if n.sender else 'System',
                    'sender_photo': (
                        n.sender.profile.profile_photo.url
                        if n.sender and hasattr(n.sender, 'profile') and n.sender.profile.profile_photo
                        else None
                    ),
                }
                for n in paginated
            ]
            return api_response(True, 'Notifications fetched.', data, 200, status.HTTP_200_OK,
                                pagination={'total': total, 'unread_count': unread_count, 'page': page, 'size': size})
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            if request.data.get('all'):
                request.user.notifications.filter(is_read=False).update(is_read=True)
                return api_response(True, 'All notifications marked as read.', None, 200, status.HTTP_200_OK)

            ids = request.data.get('notification_ids', [])
            if ids:
                Notification.objects.filter(id__in=ids, recipient=request.user).update(is_read=True)
            return api_response(True, 'Notifications marked as read.', None, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            notif = Notification.objects.get(id=pk, recipient=request.user)
            notif.delete()
            return api_response(True, 'Notification deleted.', None, 200, status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return api_response(False, 'Notification not found.', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)
