import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # We can group by user ID if authenticated
        self.user = self.scope.get("user")
        if self.user and self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}"
        else:
            self.group_name = "broadcast"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, _close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from room group
    async def send_notification(self, event):
        message = event["message"]
        title = event.get("title", "Notificación")
        type_notif = event.get("type", "info")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "title": title,
            "message": message,
            "type": type_notif
        }))
