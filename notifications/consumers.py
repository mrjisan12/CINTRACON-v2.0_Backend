import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or user.is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send unread count on connect
        from channels.db import database_sync_to_async
        unread = await database_sync_to_async(
            lambda: user.notifications.filter(is_read=False).count()
        )()
        await self.send(text_data=json.dumps({'type': 'unread_count', 'count': unread}))

    async def disconnect(self, code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Client can send {"action": "mark_read", "ids": [1,2,3]}
        try:
            data = json.loads(text_data or '{}')
            if data.get('action') == 'mark_read':
                from channels.db import database_sync_to_async
                from .models import Notification
                ids = data.get('ids', [])
                await database_sync_to_async(
                    lambda: Notification.objects.filter(
                        id__in=ids, recipient=self.scope['user']
                    ).update(is_read=True)
                )()
        except Exception:
            pass

    async def send_notification(self, event):
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification_type': data.get('notification_type'),
            'id': data.get('id'),
            'message': data.get('message'),
            'link': data.get('link'),
            'created_at': data.get('created_at'),
            'sender_name': data.get('sender_name'),
            'sender_photo': data.get('sender_photo'),
            'is_read': data.get('is_read', False),
        }))
