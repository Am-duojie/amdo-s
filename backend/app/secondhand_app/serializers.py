from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import (
    Category, Product, ProductImage, Order, Message, Favorite, Address, UserProfile, RecycleOrder,
    VerifiedProduct, VerifiedProductImage, VerifiedOrder, VerifiedFavorite, Shop
)


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    avatar = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'avatar', 'bio', 'location']
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
        fields = ['avatar', 'bio', 'location', 'updated_at']
        read_only_fields = ['updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户信息更新序列化器"""
    avatar = serializers.ImageField(required=False, write_only=True)
    bio = serializers.CharField(required=False, write_only=True, allow_blank=True)
    location = serializers.CharField(required=False, write_only=True, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'avatar', 'bio', 'location']

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
        
        # 更新头像
        if avatar_file:
            profile.avatar = avatar_file
        
        # 保存扩展信息
        profile.save()
        
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
    shop = ShopSerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    shop_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    images = ProductImageSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'category', 'category_id', 'shop', 'shop_id', 'title', 'description',
            'price', 'original_price', 'condition', 'status', 'location',
            'contact_phone', 'contact_wechat', 'view_count', 'images',
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
        shop_id = validated_data.pop('shop_id', None)
        if category_id:
            try:
                validated_data['category'] = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        if shop_id:
            try:
                validated_data['shop'] = Shop.objects.get(id=shop_id)
            except Shop.DoesNotExist:
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

    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'product', 'product_id', 'total_price', 'status',
            'shipping_address', 'shipping_name', 'shipping_phone', 'carrier', 'tracking_number', 'shipped_at', 'delivered_at', 'note',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['buyer', 'total_price', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_id": "商品不存在"})
        
        validated_data['product'] = product
        validated_data['buyer'] = self.context['request'].user
        validated_data['total_price'] = product.price
        return super().create(validated_data)


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
            'content', 'is_read', 'created_at'
        ]
        read_only_fields = ['sender', 'is_read', 'created_at']

    def create(self, validated_data):
        receiver_id = validated_data.pop('receiver_id')
        product_id = validated_data.pop('product_id', None)
        
        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"receiver_id": "接收者不存在"})
        
        validated_data['receiver'] = receiver
        validated_data['sender'] = self.context['request'].user
        
        if product_id:
            try:
                validated_data['product'] = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                pass
        
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
    
    class Meta:
        model = RecycleOrder
        fields = [
            'id', 'user', 'device_type', 'brand', 'model', 'storage',
            'condition', 'estimated_price', 'final_price', 'bonus',
            'status', 'contact_name', 'contact_phone', 'address',
            'note', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'estimated_price', 'final_price', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class VerifiedProductImageSerializer(serializers.ModelSerializer):
    """官方验货商品图片序列化器"""
    class Meta:
        model = VerifiedProductImage
        fields = ['id', 'image', 'is_primary']


class VerifiedProductSerializer(serializers.ModelSerializer):
    """官方验货商品序列化器"""
    seller = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    shop_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    images = VerifiedProductImageSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = VerifiedProduct
        fields = [
            'id', 'seller', 'category', 'category_id', 'shop', 'shop_id', 'title', 'description',
            'price', 'original_price', 'condition', 'status', 'location',
            'contact_phone', 'contact_wechat', 'brand', 'model', 'storage',
            'screen_size', 'battery_health', 'charging_type', 'verified_at',
            'verified_by', 'view_count', 'sales_count', 'images',
            'is_favorited', 'created_at', 'updated_at'
        ]
        read_only_fields = ['seller', 'view_count', 'sales_count', 'verified_at', 'verified_by', 'created_at', 'updated_at']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return VerifiedFavorite.objects.filter(user=request.user, product=obj).exists()
        return False

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        shop_id = validated_data.pop('shop_id', None)
        if category_id:
            try:
                validated_data['category'] = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        if shop_id:
            try:
                validated_data['shop'] = Shop.objects.get(id=shop_id)
            except Shop.DoesNotExist:
                pass
        validated_data.setdefault('status', 'active')
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)


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
