from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
import uuid

from .models import (
    Category, Product, ProductImage, Order, Message, Favorite, Address, UserProfile, RecycleOrder,
    VerifiedProduct, VerifiedProductImage, VerifiedOrder, VerifiedFavorite, Shop, VerifiedDevice,
    create_verified_device_from_recycle_order
)


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    avatar = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    alipay_login_id = serializers.SerializerMethodField()
    alipay_user_id = serializers.SerializerMethodField()
    alipay_real_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'avatar', 'bio', 'location', 'alipay_login_id', 'alipay_user_id', 'alipay_real_name']
        read_only_fields = ['id', 'date_joined']
    
    def get_avatar(self, obj):
        """获取用户头像"""
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return self.context['request'].build_absolute_uri(obj.profile.avatar.url) if self.context.get('request') else obj.profile.avatar.url
        return None
    
    def get_bio(self, obj):
        """获取个人简介"""
        if hasattr(obj, 'profile'):
            return obj.profile.bio
        return ''
    
    def get_location(self, obj):
        """获取所在地"""
        if hasattr(obj, 'profile'):
            return obj.profile.location
        return ''

    def get_alipay_login_id(self, obj):
        try:
            profile = obj.profile
            if profile and profile.alipay_login_id:
                return profile.alipay_login_id
        except UserProfile.DoesNotExist:
            pass
        except AttributeError:
            pass
        return ''

    def get_alipay_real_name(self, obj):
        try:
            profile = obj.profile
            if profile and profile.alipay_real_name:
                return profile.alipay_real_name
        except UserProfile.DoesNotExist:
            pass
        except AttributeError:
            pass
        return ''

    def get_alipay_user_id(self, obj):
        try:
            profile = obj.profile
            if profile and profile.alipay_user_id:
                return profile.alipay_user_id
        except UserProfile.DoesNotExist:
            pass
        except AttributeError:
            pass
        return ''


class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 'last_name']

    def validate_username(self, value):
        """验证用户名"""
        if len(value) < 3:
            raise serializers.ValidationError("用户名至少需要3个字符")
        if len(value) > 150:
            raise serializers.ValidationError("用户名不能超过150个字符")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_email(self, value):
        """验证邮箱"""
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被注册")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次密码输入不一致"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """用户扩展信息序列化器"""
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'location', 'alipay_login_id', 'alipay_user_id', 'alipay_real_name', 'updated_at']
        read_only_fields = ['updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户信息更新序列化器"""
    avatar = serializers.ImageField(required=False, write_only=True)
    bio = serializers.CharField(required=False, write_only=True, allow_blank=True)
    location = serializers.CharField(required=False, write_only=True, allow_blank=True)
    alipay_login_id = serializers.CharField(required=False, write_only=True, allow_blank=True)
    alipay_user_id = serializers.CharField(required=False, write_only=True, allow_blank=True)
    alipay_real_name = serializers.CharField(required=False, write_only=True, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'avatar', 'bio', 'location', 'alipay_login_id', 'alipay_user_id', 'alipay_real_name']

    def validate_username(self, value):
        """验证用户名"""
        if len(value) < 3:
            raise serializers.ValidationError("用户名至少需要3个字符")
        if len(value) > 150:
            raise serializers.ValidationError("用户名不能超过150个字符")
        # 检查用户名是否被其他用户使用
        if User.objects.filter(username=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_email(self, value):
        """验证邮箱"""
        if value:
            # 检查邮箱是否被其他用户使用
            if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("邮箱已被其他用户使用")
        return value
    
    def update(self, instance, validated_data):
        """更新用户信息和扩展信息"""
        # 处理扩展信息
        bio = validated_data.pop('bio', None)
        location = validated_data.pop('location', None)
        alipay_login_id = validated_data.pop('alipay_login_id', None)
        alipay_user_id = validated_data.pop('alipay_user_id', None)
        alipay_real_name = validated_data.pop('alipay_real_name', None)
        
        # 处理头像文件
        avatar_file = validated_data.pop('avatar', None)
        
        # 更新用户基本信息
        instance = super().update(instance, validated_data)
        
        # 获取或创建用户扩展信息
        profile, created = UserProfile.objects.get_or_create(user=instance)
        
        # 更新扩展信息
        if bio is not None:
            profile.bio = bio
        if location is not None:
            profile.location = location
        if alipay_login_id is not None:
            profile.alipay_login_id = alipay_login_id
        if alipay_user_id is not None:
            profile.alipay_user_id = alipay_user_id
        if alipay_real_name is not None:
            profile.alipay_real_name = alipay_real_name
        
        # 更新头像
        if avatar_file:
            profile.avatar = avatar_file
        
        # 保存扩展信息
        profile.save()
        
        try:
            if ((alipay_login_id is not None) and str(alipay_login_id).strip()) or ((alipay_user_id is not None) and str(alipay_user_id).strip()):
                from django.utils import timezone
                from .models import Order
                from app.secondhand_app.alipay_client import AlipayClient
                alipay = AlipayClient()
                qs = Order.objects.filter(product__seller=instance, status='completed').exclude(settlement_status='settled')
                for o in qs:
                    trade_no = getattr(o, 'alipay_trade_no', '')
                    if not trade_no:
                        q = alipay.query_trade(f'normal_{o.id}')
                        if q.get('success'):
                            trade_no = q.get('trade_no', '')
                    if not trade_no:
                        continue
                    from decimal import Decimal
                    seller_amount = Decimal(str(o.product.price))
                    commission_amount = Decimal(str(o.total_price)) - seller_amount
                    if commission_amount < 0:
                        commission_amount = Decimal('0.00')
                    out_request_no = f'auto_bind_settle_{o.id}_{int(timezone.now().timestamp())}'
                    if profile.alipay_user_id:
                        res = alipay.settle_order(
                            trade_no=trade_no,
                            out_request_no=out_request_no,
                            splits=[{
                                'trans_in': profile.alipay_user_id,
                                'trans_in_type': 'userId',
                                'amount': float(seller_amount),
                                'desc': '易淘分账-卖家(绑定后自动结算)',
                                'royalty_scene': '平台服务费'
                            }]
                        )
                    else:
                        res = alipay.settle_order(
                            trade_no=trade_no,
                            out_request_no=out_request_no,
                            splits=[{
                                'trans_in': profile.alipay_login_id,
                                'trans_in_type': 'loginName',
                                'amount': float(seller_amount),
                                'desc': '易淘分账-卖家(绑定后自动结算)',
                                'royalty_scene': '平台服务费'
                            }]
                        )
                    if res.get('success'):
                        o.settlement_status = 'settled'
                        o.settled_at = timezone.now()
                        o.settle_request_no = out_request_no
                        o.seller_settle_amount = seller_amount
                        o.platform_commission_amount = commission_amount
                        o.settlement_method = 'ROYALTY'
                    else:
                        o.settlement_status = 'failed'
                        o.settle_request_no = out_request_no
                        try:
                            from django.conf import settings
                            if getattr(settings, 'SETTLEMENT_FALLBACK_TO_TRANSFER', False):
                                out_biz_no = f'auto_bind_settle_transfer_{o.id}_{int(timezone.now().timestamp())}'
                                transfer_res = alipay.transfer_to_account(
                                    out_biz_no=out_biz_no,
                                    payee_account=(profile.alipay_login_id or profile.alipay_user_id),
                                    amount=float(seller_amount),
                                    payee_real_name=profile.alipay_real_name,
                                    remark='易淘分账-绑定后转账代结算'
                                )
                                if transfer_res.get('success'):
                                    o.settlement_status = 'settled'
                                    o.settled_at = timezone.now()
                                    o.seller_settle_amount = seller_amount
                                    o.platform_commission_amount = commission_amount
                                    o.settlement_method = 'TRANSFER'
                                    o.transfer_order_id = transfer_res.get('order_id','')
                        except Exception:
                            pass
                    o.save()
                    try:
                        from app.secondhand_app.models import Wallet, WalletTransaction
                        wallet, _ = Wallet.objects.get_or_create(user=profile.user)
                        WalletTransaction.objects.create(
                            wallet=wallet,
                            transaction_type='income',
                            amount=seller_amount,
                            balance_after=wallet.balance,
                            related_market_order=o,
                            alipay_account=(profile.alipay_user_id or profile.alipay_login_id),
                            alipay_name=profile.alipay_real_name,
                            alipay_order_id=getattr(o,'transfer_order_id',''),
                            note=f'订单#{o.id} 结算完成，资金已存入支付宝: {(profile.alipay_user_id or profile.alipay_login_id)}'
                        )
                    except Exception:
                        pass
        except Exception:
            pass

        return instance


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    product_count = serializers.IntegerField(read_only=True, help_text='该分类下的商品数量（热度）')
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'product_count', 'created_at']


class ShopSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    class Meta:
        model = Shop
        fields = ['id','owner','name','description','logo','address','contact_phone','status','rating','is_verified','created_at','updated_at']
        read_only_fields = ['owner','created_at','updated_at']


class ProductImageSerializer(serializers.ModelSerializer):
    """商品图片序列化器"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary']


class ProductSerializer(serializers.ModelSerializer):
    """商品序列化器"""
    seller = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    images = ProductImageSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    favorite_count = serializers.IntegerField(read_only=True)
    recommend_score = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'category', 'category_id', 'title', 'description',
            'price', 'original_price', 'condition', 'status', 'location',
            'view_count', 'favorite_count', 'recommend_score', 'images',
            'is_favorited', 'created_at', 'updated_at'
        ]
        read_only_fields = ['seller', 'view_count', 'created_at', 'updated_at']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, product=obj).exists()
        return False

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id:
            try:
                validated_data['category'] = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        # 显式设置为在售，避免默认值或前端缺省导致的状态异常
        validated_data.setdefault('status', 'active')
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""
    buyer = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    settlement_account = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'product', 'product_id', 'total_price', 'status',
            'shipping_address', 'shipping_name', 'shipping_phone', 'carrier', 'tracking_number', 'shipped_at', 'delivered_at', 'note',
            'alipay_trade_no', 'settlement_status', 'settled_at', 'settle_request_no', 'seller_settle_amount', 'platform_commission_amount',
            'settlement_method', 'transfer_order_id', 'settlement_account',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['buyer', 'total_price', 'status', 'alipay_trade_no', 'settlement_status', 'settled_at', 'settle_request_no', 'seller_settle_amount', 'platform_commission_amount', 'settlement_method', 'transfer_order_id', 'settlement_account', 'created_at', 'updated_at']

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_id": "商品不存在"})
        
        validated_data['product'] = product
        validated_data['buyer'] = self.context['request'].user
        # 引入平台佣金（如启用）
        from django.conf import settings
        commission_rate = getattr(settings, 'PLATFORM_COMMISSION_RATE', 0)
        if getattr(settings, 'ENABLE_ALIPAY_ROYALTY', False) and commission_rate > 0:
            from decimal import Decimal
            base = Decimal(str(product.price))
            commission = (base * Decimal(str(commission_rate))).quantize(Decimal('0.01'))
            validated_data['total_price'] = base + commission
            validated_data['platform_commission_amount'] = commission
            validated_data['seller_settle_amount'] = base
            validated_data['settlement_status'] = 'pending'
        else:
            validated_data['total_price'] = product.price
        return super().create(validated_data)

    def get_settlement_account(self, obj):
        try:
            profile = obj.product.seller.profile
            return profile.alipay_user_id or profile.alipay_login_id or ''
        except Exception:
            return ''


class MessageSerializer(serializers.ModelSerializer):
    """消息序列化器"""
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    receiver_id = serializers.IntegerField(write_only=True)
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'receiver', 'receiver_id', 'product', 'product_id',
            'content', 'is_read', 'created_at', 'updated_at', 'message_type', 'image', 'payload',
            'recalled', 'recallable_until'
        ]
        read_only_fields = ['sender', 'is_read', 'created_at', 'updated_at', 'recalled', 'recallable_until']

    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta

        receiver_id = validated_data.pop('receiver_id')
        product_id = validated_data.pop('product_id', None)
        message_type = validated_data.get('message_type', 'text') or 'text'
        payload = validated_data.get('payload') or {}

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"receiver_id": "接收者不存在"})

        validated_data['receiver'] = receiver
        validated_data['sender'] = self.context['request'].user

        product = None
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                validated_data['product'] = product
            except Product.DoesNotExist:
                raise serializers.ValidationError({"product_id": "商品不存在"})

        # 如果是商品消息，补全快照
        if message_type == 'product' and product:
            payload = payload or {}
            payload.update({
                'product_id': product.id,
                'title': product.title,
                'price': str(product.price),
                'cover': product.images.filter(is_primary=True).first().image.url if hasattr(product, 'images') else '',
                'status': product.status,
            })
            validated_data['payload'] = payload

        # 撤回窗口默认 2 分钟
        validated_data['recallable_until'] = timezone.now() + timedelta(minutes=2)
        return super().create(validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    """收藏序列化器"""
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'product_id', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_id": "商品不存在"})
        
        validated_data['product'] = product
        validated_data['user'] = self.context['request'].user
        
        # 检查是否已收藏
        if Favorite.objects.filter(user=validated_data['user'], product=product).exists():
            raise serializers.ValidationError({"product_id": "该商品已收藏"})
        
        return super().create(validated_data)


class AddressSerializer(serializers.ModelSerializer):
    """收货地址序列化器"""
    class Meta:
        model = Address
        fields = [
            'id', 'name', 'phone', 'province', 'city', 
            'district', 'detail_address', 'is_default', 'created_at'
        ]
        read_only_fields = ['created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        
        # 如果设置为默认地址，将其他地址设置为非默认
        if validated_data.get('is_default', False):
            Address.objects.filter(user=validated_data['user']).update(is_default=False)
            
        # 如果是第一个地址，自动设为默认
        if not Address.objects.filter(user=validated_data['user']).exists():
            validated_data['is_default'] = True
            
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 如果更新为默认地址，将其他地址设置为非默认
        if validated_data.get('is_default', False) and not instance.is_default:
            Address.objects.filter(user=instance.user).exclude(id=instance.id).update(is_default=False)
            
        return super().update(instance, validated_data)


class RecycleOrderSerializer(serializers.ModelSerializer):
    """回收订单序列化器"""
    user = UserSerializer(read_only=True)
    template_info = serializers.SerializerMethodField()
    
    class Meta:
        model = RecycleOrder
        fields = [
            'id', 'user', 'template', 'template_info',
            'device_type', 'brand', 'model', 'storage',
            'selected_storage', 'selected_color', 'selected_ram', 'selected_version',
            'questionnaire_answers',
            'condition', 'estimated_price', 'final_price', 'bonus',
            'status', 'contact_name', 'contact_phone', 'address',
            'note', 'shipping_carrier', 'tracking_number', 'shipped_at',
            'received_at', 'inspected_at', 'paid_at', 'payment_status',
            'payment_method', 'payment_account', 'payment_note',
            'price_dispute', 'price_dispute_reason', 'reject_reason', 'final_price_confirmed', 'payment_retry_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'final_price', 'received_at', 
                           'inspected_at', 'paid_at', 'created_at', 'updated_at']
    
    def get_template_info(self, obj):
        """获取模板基本信息"""
        if obj.template:
            return {
                'id': obj.template.id,
                'device_type': obj.template.device_type,
                'brand': obj.template.brand,
                'model': obj.template.model,
                'series': obj.template.series or '',
            }
        return None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # 允许在创建时设置 estimated_price（从请求数据中获取）
        request = self.context.get('request')
        if request and 'estimated_price' in request.data:
            try:
                validated_data['estimated_price'] = float(request.data['estimated_price'])
            except (ValueError, TypeError):
                pass  # 如果转换失败，使用默认值（null）
        # 设置初始状态为 'pending'（待估价），用户提交订单后处于待估价状态
        validated_data['status'] = 'pending'
        # 不设置寄出时间，等用户填写物流信息后再设置
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """更新订单，支持用户操作的状态流转"""
        # 获取当前状态和新状态
        current_status = instance.status
        new_status = validated_data.get('status', current_status)

        request = self.context.get('request')
        is_user_update = bool(request and getattr(request, 'user', None) and request.user.is_authenticated)

        # 用户确认价格后，不允许再提交异议或取消订单（避免已进入打款流程后回退）
        if is_user_update and instance.final_price_confirmed:
          if validated_data.get('price_dispute') is True or 'price_dispute_reason' in validated_data:
            raise serializers.ValidationError({'price_dispute': '已确认最终价格，无法再提交价格异议'})
          if validated_data.get('status') == 'cancelled':
            raise serializers.ValidationError({'status': '已确认最终价格，无法取消订单'})
        
        # 如果用户填写了物流信息，自动将状态从 pending 变为 shipped
        if current_status == 'pending' and 'shipping_carrier' in validated_data and 'tracking_number' in validated_data:
            if validated_data.get('shipping_carrier') and validated_data.get('tracking_number'):
                validated_data['status'] = 'shipped'
                from django.utils import timezone
                if not instance.shipped_at:
                    validated_data['shipped_at'] = timezone.now()
        
        # 定义允许的状态流转规则（用户操作）
        # 流程：待估价 -> 已寄出（用户填写物流） -> 已收货（平台操作） -> 已检测 -> 已完成
        allowed_transitions = {
            'pending': ['cancelled'],
            'shipped': ['cancelled'],  # 用户可以在已寄出状态取消订单
            # 已检测/已完成需通过“确认最终价格”接口完成，不允许直接改状态
        }
        
        # 如果状态发生变化，检查是否允许
        if new_status != current_status:
            allowed_next = allowed_transitions.get(current_status, [])
            if new_status not in allowed_next:
                # 如果不在允许的流转中，检查是否是管理员操作（通过其他字段判断）
                # 或者保持原状态不变
                if new_status not in ['pending', 'shipped', 'received', 'inspected', 'completed', 'cancelled']:
                    raise serializers.ValidationError({
                        'status': f'不允许从 {current_status} 状态转换到 {new_status} 状态。允许的转换：{allowed_next}'
                    })
                # 如果是管理员操作的状态（如从shipped到inspected），允许通过
                # 但这里我们只处理用户操作，管理员操作应该通过admin API
        
        # 如果状态变为shipped，自动设置shipped_at（如果还没有设置）
        if new_status == 'shipped' and not instance.shipped_at:
            from django.utils import timezone
            if 'shipped_at' not in validated_data:
                validated_data['shipped_at'] = timezone.now()
        
        # 确保联系信息被正确保存
        # 这些字段已经在fields中定义，应该可以正常更新
        updated_order = super().update(instance, validated_data)

        # 自动：收货/质检/完成后，生成官方验库存（避免重复）
        if updated_order.status in ['received', 'inspected', 'completed']:
            try:
                create_verified_device_from_recycle_order(updated_order)
            except Exception:
                # 避免影响主流程，失败可在后台查看日志后手动触发
                pass

        return updated_order


class VerifiedProductImageSerializer(serializers.ModelSerializer):
    """官方验货商品图片序列化器"""
    class Meta:
        model = VerifiedProductImage
        fields = ['id', 'image', 'is_primary']


class VerifiedDeviceSerializer(serializers.ModelSerializer):
    """官方验库存单品序列化器"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    seller = UserSerializer(read_only=True)

    class Meta:
        model = VerifiedDevice
        fields = [
            'id', 'sn', 'imei', 'brand', 'model', 'storage', 'condition', 'status',
            'location', 'barcode', 'cost_price', 'suggested_price',
            'cover_image', 'detail_images', 'inspection_reports',
            'inspection_result', 'inspection_date', 'inspection_staff', 'inspection_note',
            'battery_health', 'screen_condition', 'repair_history',
            'recycle_order', 'category', 'category_id', 'seller',
            'linked_product', 'created_at', 'updated_at'
        ]
        read_only_fields = ['seller', 'linked_product', 'created_at', 'updated_at']

    def validate(self, attrs):
        category_id = attrs.get('category_id')
        if category_id:
            try:
                attrs['category'] = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                raise serializers.ValidationError({'category_id': '分类不存在'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('category_id', None)
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data.setdefault('seller', request.user)
        # 如果前端未录入 SN/IMEI，允许在演示模式下自动生成占位 SN，避免强制输入
        if not validated_data.get('sn'):
            validated_data['sn'] = f"AUTO-{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('category_id', None)
        return super().update(instance, validated_data)


class VerifiedProductSerializer(serializers.ModelSerializer):
    """官方验货商品序列化器"""
    seller = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    images = VerifiedProductImageSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    cover_image = serializers.CharField(required=False, allow_blank=True)
    detail_images = serializers.ListField(child=serializers.CharField(), required=False)
    inspection_reports = serializers.JSONField(required=False)
    inspection_result = serializers.ChoiceField(choices=[('pass','pass'),('warn','warn'),('fail','fail')], required=False)
    inspection_date = serializers.DateField(required=False, allow_null=True)
    inspection_staff = serializers.CharField(required=False, allow_blank=True)
    inspection_note = serializers.CharField(required=False, allow_blank=True)
    stock = serializers.IntegerField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = VerifiedProduct
        fields = [
            'id', 'seller', 'category', 'category_id', 'title', 'description',
            'price', 'original_price', 'condition', 'status', 'device_type',
            'brand', 'model', 'storage', 'ram', 'version', 'repair_status',
            'screen_size', 'battery_health', 'charging_type', 'verified_at',
            'verified_by', 'view_count', 'sales_count', 'images',
            'is_favorited', 'created_at', 'updated_at',
            'cover_image', 'detail_images', 'inspection_reports',
            'inspection_result', 'inspection_date', 'inspection_staff', 'inspection_note',
            'stock', 'tags', 'published_at', 'removed_reason', 'template'
        ]
        read_only_fields = ['seller', 'view_count', 'sales_count', 'verified_at', 'verified_by', 'created_at', 'updated_at']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return VerifiedFavorite.objects.filter(user=request.user, product=obj).exists()
        return False

    def validate(self, attrs):
        # 基础必填校验
        if self.instance is None:  # create
            required_fields = ['title', 'brand', 'model', 'price', 'condition']
            for f in required_fields:
                if attrs.get(f) in [None, '', []]:
                    raise serializers.ValidationError({f: '必填'})
        # 分类校验（可选，但有值则必须是有效ID）
        category_id = attrs.get('category_id')
        if category_id:
            try:
                Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                raise serializers.ValidationError({'category_id': '分类不存在'})
        price = attrs.get('price') if 'price' in attrs else getattr(self.instance, 'price', None)
        if price is not None and price <= 0:
            raise serializers.ValidationError({'price': '价格必须大于0'})
        stock = attrs.get('stock') if 'stock' in attrs else getattr(self.instance, 'stock', 1)
        if stock is not None and stock < 1:
            raise serializers.ValidationError({'stock': '库存至少为1'})
        detail_images = attrs.get('detail_images')
        # 放宽详情图限制，至少 1 张即可，避免阻塞保存
        if detail_images is not None and len(detail_images) < 1:
            raise serializers.ValidationError({'detail_images': '请至少上传1张详情图'})
        inspection_reports = attrs.get('inspection_reports')
        if inspection_reports is not None and len(inspection_reports) > 3:
            raise serializers.ValidationError({'inspection_reports': '质检报告最多3个'})
        return attrs

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id:
            try:
                validated_data['category'] = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        validated_data.setdefault('status', 'draft')
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        # 允许前端传字符串/空列表，做清洗
        if 'detail_images' in validated_data and validated_data['detail_images'] is None:
            validated_data['detail_images'] = []
        if 'inspection_reports' in validated_data and validated_data['inspection_reports'] is None:
            validated_data['inspection_reports'] = []
        if category_id:
            try:
                validated_data['category'] = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        return super().update(instance, validated_data)


class VerifiedOrderSerializer(serializers.ModelSerializer):
    """官方验货订单序列化器"""
    buyer = UserSerializer(read_only=True)
    product = VerifiedProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = VerifiedOrder
        fields = [
            'id', 'buyer', 'product', 'product_id', 'total_price', 'status',
            'shipping_address', 'shipping_name', 'shipping_phone', 'carrier', 'tracking_number', 'shipped_at', 'delivered_at', 'note',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['buyer', 'total_price', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        try:
            product = VerifiedProduct.objects.get(id=product_id)
        except VerifiedProduct.DoesNotExist:
            raise serializers.ValidationError({"product_id": "商品不存在"})
        
        validated_data['product'] = product
        validated_data['buyer'] = self.context['request'].user
        validated_data['total_price'] = product.price
        return super().create(validated_data)


class VerifiedFavoriteSerializer(serializers.ModelSerializer):
    """官方验货收藏序列化器"""
    user = UserSerializer(read_only=True)
    product = VerifiedProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = VerifiedFavorite
        fields = ['id', 'user', 'product', 'product_id', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        try:
            product = VerifiedProduct.objects.get(id=product_id)
        except VerifiedProduct.DoesNotExist:
            raise serializers.ValidationError({"product_id": "商品不存在"})
        
        validated_data['product'] = product
        validated_data['user'] = self.context['request'].user
        
        # 检查是否已收藏
        if VerifiedFavorite.objects.filter(user=validated_data['user'], product=product).exists():
            raise serializers.ValidationError({"product_id": "该商品已收藏"})
        
        return super().create(validated_data)



# ==================== 回收机型模板序列化器（用户端） ====================

class RecycleQuestionOptionPublicSerializer(serializers.Serializer):
    """问卷选项序列化器（用户端）"""
    value = serializers.CharField()
    label = serializers.CharField()
    desc = serializers.CharField(allow_blank=True)
    impact = serializers.CharField(allow_blank=True)


class RecycleQuestionPublicSerializer(serializers.Serializer):
    """问卷问题序列化器（用户端）"""
    key = serializers.CharField()
    title = serializers.CharField()
    helper = serializers.CharField(allow_blank=True)
    question_type = serializers.CharField()
    is_required = serializers.BooleanField()
    options = RecycleQuestionOptionPublicSerializer(many=True)


class RecycleDeviceTemplateCatalogSerializer(serializers.Serializer):
    """机型目录序列化器（用户端）- 用于列表展示"""
    id = serializers.IntegerField()
    device_type = serializers.CharField()
    brand = serializers.CharField()
    model = serializers.CharField()
    series = serializers.CharField(allow_blank=True)
    storages = serializers.ListField(child=serializers.CharField())
    base_prices = serializers.DictField()
    default_cover_image = serializers.CharField(allow_blank=True)
    screen_size = serializers.CharField(allow_blank=True)
    battery_capacity = serializers.CharField(allow_blank=True)
    charging_type = serializers.CharField(allow_blank=True)


class RecycleDeviceTemplateDetailSerializer(serializers.Serializer):
    """机型详情序列化器（用户端）- 包含完整信息"""
    id = serializers.IntegerField()
    device_type = serializers.CharField()
    brand = serializers.CharField()
    model = serializers.CharField()
    series = serializers.CharField(allow_blank=True)
    storages = serializers.ListField(child=serializers.CharField())
    base_prices = serializers.DictField()
    ram_options = serializers.ListField(child=serializers.CharField())
    version_options = serializers.ListField(child=serializers.CharField())
    color_options = serializers.ListField(child=serializers.CharField())
    screen_size = serializers.CharField(allow_blank=True)
    battery_capacity = serializers.CharField(allow_blank=True)
    charging_type = serializers.CharField(allow_blank=True)
    default_cover_image = serializers.CharField(allow_blank=True)
    default_detail_images = serializers.ListField(child=serializers.CharField())
    description_template = serializers.CharField(allow_blank=True)
