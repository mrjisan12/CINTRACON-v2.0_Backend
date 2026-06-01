from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification


def create_notification(recipient, sender, notif_type, message, link=''):
    """Create a DB notification and push via WebSocket."""
    if recipient == sender:
        return None

    notif = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notif_type=notif_type,
        message=message,
        link=link,
    )

    # Push real-time notification via Channels
    try:
        channel_layer = get_channel_layer()
        payload = {
            'id': notif.id,
            'notification_type': notif_type,
            'message': message,
            'link': link,
            'sender_name': sender.full_name if sender else 'System',
            'sender_photo': sender.profile.profile_photo.url if (sender and sender.profile.profile_photo) else None,
            'created_at': notif.created_at.isoformat(),
            'is_read': False,
        }
        async_to_sync(channel_layer.group_send)(
            f"user_{recipient.id}",
            {'type': 'send_notification', 'data': payload},
        )
    except Exception:
        pass

    return notif
