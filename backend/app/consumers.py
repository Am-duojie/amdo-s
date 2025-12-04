import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from app.secondhand_app.models import Message, Product
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 从查询参数中获取token
        query_string = self.scope['query_string'].decode()
        token = None
        
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break
        
        if not token:
            await self.close()
            return
        
        # 验证token
        try:
            token_obj = await database_sync_to_async(Token.objects.get)(key=token)
            self.user = await database_sync_to_async(User.objects.get)(id=token_obj.user_id)
        except:
            await self.close()
            return
        
        self.user_group_name = f'user_{self.user.id}'
        
        # 加入用户组
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # 离开用户组
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            # 处理消息发送
            if data.get('type') == 'chat_message':
                await self.handle_chat_message(data)
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def handle_chat_message(self, data):
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        product_id = data.get('product_id')
        
        if not receiver_id or not content:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Missing receiver_id or content'
            }))
            return
        
        try:
            # 创建消息
            receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)
            product = None
            if product_id:
                try:
                    product = await database_sync_to_async(Product.objects.get)(id=product_id)
                except Product.DoesNotExist:
                    pass
            
            message = await database_sync_to_async(Message.objects.create)(
                sender=self.user,
                receiver=receiver,
                content=content,
                product=product
            )
            
            # 准备发送数据
            message_data = {
                'type': 'new_message',
                'id': message.id,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'receiver_id': receiver.id,
                'receiver_username': receiver.username,
                'content': content,
                'product_id': product_id,
                'product_title': product.title if product else None,
                'created_at': message.created_at.isoformat(),
                'is_read': False
            }
            
            # 发送给发送者
            await self.channel_layer.group_send(
                self.user_group_name,
                message_data
            )
            
            # 发送给接收者
            receiver_group_name = f'user_{receiver_id}'
            await self.channel_layer.group_send(
                receiver_group_name,
                message_data
            )
            
        except User.DoesNotExist:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Receiver not found'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to send message: {str(e)}'
            }))
    
    async def chat_message(self, event):
        # 发送消息到WebSocket
        await self.send(text_data=json.dumps(event))