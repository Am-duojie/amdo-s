import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from app.secondhand_app.models import Message, Product, ProductImage
from django.utils import timezone
from datetime import timedelta
import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    def _get_product_cover(self, product_id):
        if not product_id:
            return ''
        try:
            primary = ProductImage.objects.filter(product_id=product_id, is_primary=True).first()
            if primary and primary.image:
                return primary.image.url
            fallback = ProductImage.objects.filter(product_id=product_id).first()
            if fallback and fallback.image:
                return fallback.image.url
        except Exception:
            return ''
        return ''

    async def connect(self):
        # 从查询参数中获取token
        query_string = self.scope['query_string'].decode()
        token = None
        logger.info(f"WebSocket连接尝试，query={query_string}")
        
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break
        
        if not token:
            logger.warning("WebSocket拒绝：缺少token")
            await self.close()
            return
        
        # 验证token：优先尝试 DRF Token，失败则回退 JWT (SimpleJWT)
        user = None
        drf_error = None
        try:
            from rest_framework.authtoken.models import Token as DRFToken
            if hasattr(DRFToken, 'objects'):
                token_obj = await database_sync_to_async(DRFToken.objects.select_related('user').get)(key=token)
                user = token_obj.user
        except Exception as e:
            drf_error = e

        if user is None:
            try:
                jwt_auth = JWTAuthentication()
                validated = jwt_auth.get_validated_token(token)
                user = await database_sync_to_async(jwt_auth.get_user)(validated)
            except (InvalidToken, TokenError, Exception) as e:
                logger.warning(f"WebSocket拒绝：token无效 drf_err={drf_error} jwt_err={e}")
                await self.close()
                return

        self.user = user
        
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
        content = data.get('content', '')
        product_id = data.get('product_id')
        message_type = data.get('message_type', 'text') or 'text'
        
        if not receiver_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Missing receiver_id'
            }))
            return
        if message_type == 'text' and not content:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Content is required for text message'
            }))
            return
        
        try:
            receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)
        except User.DoesNotExist:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Receiver not found'
            }))
            return

        # 禁止自发自收，避免无意义循环
        if receiver.id == self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Cannot send message to yourself'
            }))
            return

        product = None
        if product_id:
            try:
                product = await database_sync_to_async(Product.objects.get)(id=product_id)
            except Product.DoesNotExist:
                pass

        # 构建 payload（商品消息）
        message_type = data.get('message_type', 'text') or 'text'
        payload = data.get('payload') or {}
        if message_type == 'product' and product:
            cover = await database_sync_to_async(self._get_product_cover)(product.id)
            payload.update({
                'product_id': product.id,
                'title': product.title,
                'price': str(product.price),
                'cover': cover,
                'status': product.status,
            })

        # 创建消息
        message = await database_sync_to_async(Message.objects.create)(
            sender=self.user,
            receiver=receiver,
            content=content or '',
            product=product,
            message_type=message_type,
            payload=payload,
            recallable_until=timezone.now() + timedelta(minutes=2)
        )

        # 准备发送数据（发给双方）
        payload_to_send = {
            'type': 'new_message',
            'id': message.id,
            'sender_id': self.user.id,
            'sender_username': self.user.username,
            'receiver_id': receiver.id,
            'receiver_username': receiver.username,
            'content': content,
            'product_id': product_id,
            'product_title': product.title if product else None,
            'message_type': message.message_type,
            'payload': message.payload,
            'created_at': message.created_at.isoformat(),
            'is_read': False,
            'recalled': False,
        }

        await self.channel_layer.group_send(
            self.user_group_name,
            {'type': 'chat_message', 'message': payload_to_send}
        )
        await self.channel_layer.group_send(
            f'user_{receiver_id}',
            {'type': 'chat_message', 'message': payload_to_send}
        )
    
    async def chat_message(self, event):
        # 发送消息到WebSocket
        await self.send(text_data=json.dumps(event.get('message', {})))
