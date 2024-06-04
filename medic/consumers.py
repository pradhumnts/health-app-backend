# my_app/consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer 

logger = logging.getLogger(__name__)

class BookingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        self.booking_id = self.scope['url_route']['kwargs'].get('booking_id')
        self.booking_group_name = f'booking_{self.booking_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.booking_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send(text_data=json.dumps({
            'message': f'WebSocket connection opened for booking {self.booking_id} on group {self.booking_group_name}.'
        }))
        
        logger.debug(f"WebSocket connection opened for booking {self.booking_id} on group {self.booking_group_name}")

    async def disconnect(self, close_code):
        # Ensure the group name is set
        if hasattr(self, 'booking_group_name'):
            # Leave room group
            await self.channel_layer.group_discard(
                self.booking_group_name,
                self.channel_name
            )
            logger.debug(f"WebSocket connection closed for booking {self.booking_id} with code {close_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        logger.debug(f"WebSocket message received for booking {self.booking_id}: {message}")

        # Send message to room group
        if hasattr(self, 'booking_group_name'):
            await self.channel_layer.group_send(
                self.booking_group_name,
                {
                    'type': 'booking_update',
                    'message': message
                }
            )

    async def booking_update(self, event):
        message = event['message']
        logger.debug(f"WebSocket booking update for booking {self.booking_id}: {message}")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

class ChatConsumer(WebsocketConsumer):
    
    def connect(self): 
        
        self.accept()
        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'You are now connected.'
        }))