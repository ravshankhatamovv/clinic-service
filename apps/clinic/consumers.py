# apps/clinic/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NurseNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group_name = f"nurse_{user_id}"  

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def notify(self, event):
        
        await self.send(text_data=json.dumps({
            "type": "note_notification",
            "message": event["message"],
            "patient_id": event["patient_id"],
            "patient_first_name": event["patient_first_name"],
            "patient_last_name":event["patient_last_name"]
        }))
