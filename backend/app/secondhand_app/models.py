from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """商品分类"""
    name = models.CharField(max_length=50, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """商品"""
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('active', '在售'),
        ('sold', '已售出'),
        ('removed', '已下架'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', verbose_name='卖家')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name='分类')
    title = models.CharField(max_length=200, verbose_name='商品标题')
    description = models.TextField(verbose_name='商品描述')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='原价')
    condition = models.CharField(max_length=20, choices=[
        ('new', '全新'),
        ('like_new', '几乎全新'),
        ('good', '良好'),
        ('fair', '一般'),
        ('poor', '较差')
    ], default='good', verbose_name='成色')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    location = models.CharField(max_length=100, verbose_name='所在地')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    contact_wechat = models.CharField(max_length=50, blank=True, verbose_name='微信')
    view_count = models.IntegerField(default=0, verbose_name='浏览次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    """商品图片"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='商品')
    image = models.ImageField(upload_to='products/', verbose_name='图片')
    is_primary = models.BooleanField(default=False, verbose_name='主图')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    class Meta:
        verbose_name = '商品图片'
        verbose_name_plural = '商品图片'
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"{self.product.title} - 图片"


class Order(models.Model):
    """订单"""
    STATUS_CHOICES = [
        ('pending', '待付款'),
        ('paid', '已付款'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='买家')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders', verbose_name='商品')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总价')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    shipping_address = models.TextField(verbose_name='收货地址')
    shipping_name = models.CharField(max_length=50, verbose_name='收货人姓名')
    shipping_phone = models.CharField(max_length=20, verbose_name='收货人电话')
    note = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']

    def __str__(self):
        return f"订单 #{self.id} - {self.product.title}"


class Message(models.Model):
    """消息/聊天"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name='接收者')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='messages', verbose_name='关联商品')
    content = models.TextField(verbose_name='消息内容')
    is_read = models.BooleanField(default=False, verbose_name='已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')

    class Meta:
        verbose_name = '消息'
        verbose_name_plural = '消息'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"


class Favorite(models.Model):
    """收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='用户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites', verbose_name='商品')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.product.title}"


class Address(models.Model):
    """收货地址"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    name = models.CharField(max_length=50, verbose_name='收货人姓名')
    phone = models.CharField(max_length=20, verbose_name='收货人电话')
    province = models.CharField(max_length=50, verbose_name='省')
    city = models.CharField(max_length=50, verbose_name='市')
    district = models.CharField(max_length=50, verbose_name='区/县')
    detail_address = models.TextField(verbose_name='详细地址')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '收货地址'
        verbose_name_plural = '收货地址'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.detail_address}"


class UserProfile(models.Model):
    """用户扩展信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    location = models.CharField(max_length=100, blank=True, verbose_name='所在地')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户扩展信息'
        verbose_name_plural = '用户扩展信息'

    def __str__(self):
        return f"{self.user.username}的扩展信息"


class RecycleOrder(models.Model):
    """回收订单"""
    STATUS_CHOICES = [
        ('pending', '待估价'),
        ('quoted', '已估价'),
        ('confirmed', '已确认'),
        ('shipped', '已寄出'),
        ('inspected', '已检测'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recycle_orders', verbose_name='用户')
    device_type = models.CharField(max_length=50, verbose_name='设备类型')  # 手机、平板、笔记本等
    brand = models.CharField(max_length=50, verbose_name='品牌')  # 苹果、华为、小米等
    model = models.CharField(max_length=100, verbose_name='型号')  # iPhone 13、华为Mate 60等
    storage = models.CharField(max_length=50, blank=True, verbose_name='存储容量')  # 128GB、256GB等
    condition = models.CharField(max_length=20, choices=[
        ('new', '全新'),
        ('like_new', '几乎全新'),
        ('good', '良好'),
        ('fair', '一般'),
        ('poor', '较差')
    ], default='good', verbose_name='成色')
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='预估价格')
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='最终价格')
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='加价')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    contact_name = models.CharField(max_length=50, verbose_name='联系人姓名')
    contact_phone = models.CharField(max_length=20, verbose_name='联系电话')
    address = models.TextField(verbose_name='收货地址')
    note = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '回收订单'
        verbose_name_plural = '回收订单'
        ordering = ['-created_at']

    def __str__(self):
        return f"回收订单 #{self.id} - {self.brand} {self.model}"


class VerifiedProduct(models.Model):
    """官方验货商品"""
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('active', '在售'),
        ('sold', '已售出'),
        ('removed', '已下架'),
    ]

    CONDITION_CHOICES = [
        ('new', '全新'),
        ('like_new', '99成新'),
        ('good', '95成新'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verified_products', verbose_name='卖家')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='verified_products', verbose_name='分类')
    title = models.CharField(max_length=200, verbose_name='商品标题')
    description = models.TextField(verbose_name='商品描述')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='原价')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good', verbose_name='成色')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    location = models.CharField(max_length=100, verbose_name='所在地')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    contact_wechat = models.CharField(max_length=50, blank=True, verbose_name='微信')
    
    # 官方验货特有字段
    brand = models.CharField(max_length=50, blank=True, verbose_name='品牌')  # 苹果、华为、小米等
    model = models.CharField(max_length=100, blank=True, verbose_name='型号')  # iPhone 13、华为Mate 60等
    storage = models.CharField(max_length=50, blank=True, verbose_name='存储容量')  # 128GB、256GB等
    screen_size = models.CharField(max_length=20, blank=True, verbose_name='屏幕尺寸')
    battery_health = models.CharField(max_length=20, blank=True, verbose_name='电池健康度')
    charging_type = models.CharField(max_length=50, blank=True, verbose_name='充电方式')
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name='验货时间')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_products_verified', verbose_name='验货人')
    
    view_count = models.IntegerField(default=0, verbose_name='浏览次数')
    sales_count = models.IntegerField(default=0, verbose_name='销量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '官方验货商品'
        verbose_name_plural = '官方验货商品'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class VerifiedProductImage(models.Model):
    """官方验货商品图片"""
    product = models.ForeignKey(VerifiedProduct, on_delete=models.CASCADE, related_name='images', verbose_name='商品')
    image = models.ImageField(upload_to='verified_products/', verbose_name='图片')
    is_primary = models.BooleanField(default=False, verbose_name='主图')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    class Meta:
        verbose_name = '官方验货商品图片'
        verbose_name_plural = '官方验货商品图片'
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"{self.product.title} - 图片"


class VerifiedOrder(models.Model):
    """官方验货订单"""
    STATUS_CHOICES = [
        ('pending', '待付款'),
        ('paid', '已付款'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verified_orders', verbose_name='买家')
    product = models.ForeignKey(VerifiedProduct, on_delete=models.CASCADE, related_name='orders', verbose_name='商品')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总价')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    shipping_address = models.TextField(verbose_name='收货地址')
    shipping_name = models.CharField(max_length=50, verbose_name='收货人姓名')
    shipping_phone = models.CharField(max_length=20, verbose_name='收货人电话')
    note = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '官方验货订单'
        verbose_name_plural = '官方验货订单'
        ordering = ['-created_at']

    def __str__(self):
        return f"验货订单 #{self.id} - {self.product.title}"


class VerifiedFavorite(models.Model):
    """官方验货收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verified_favorites', verbose_name='用户')
    product = models.ForeignKey(VerifiedProduct, on_delete=models.CASCADE, related_name='favorites', verbose_name='商品')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    class Meta:
        verbose_name = '官方验货收藏'
        verbose_name_plural = '官方验货收藏'
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.product.title}"