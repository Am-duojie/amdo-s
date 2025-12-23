from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """商品分类"""
    name = models.CharField(max_length=50, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    type = models.CharField(max_length=20, default='digital', verbose_name='分类类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'
        ordering = ['name']

    def __str__(self):
        return self.name


class Shop(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops', verbose_name='店主')
    name = models.CharField(max_length=100, verbose_name='店铺名称')
    description = models.TextField(blank=True, verbose_name='店铺描述')
    logo = models.ImageField(upload_to='shops/', null=True, blank=True, verbose_name='店铺Logo')
    address = models.CharField(max_length=200, blank=True, verbose_name='店铺地址')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    status = models.CharField(max_length=20, choices=[('active','正常'),('suspended','停用'),('closed','关闭')], default='active', verbose_name='状态')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name='评分')
    is_verified = models.BooleanField(default=False, verbose_name='已认证')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '店铺'
        verbose_name_plural = '店铺'
        ordering = ['-created_at']

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
    carrier = models.CharField(max_length=50, blank=True, verbose_name='物流承运商')
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name='物流单号')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='发货时间')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='签收时间')
    note = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    # 支付/分账扩展字段
    alipay_trade_no = models.CharField(max_length=64, blank=True, verbose_name='支付宝交易号')
    settlement_status = models.CharField(max_length=20, choices=[('pending','待分账'),('settled','已分账'),('failed','分账失败')], default='pending', verbose_name='分账状态')
    settled_at = models.DateTimeField(null=True, blank=True, verbose_name='分账时间')
    settle_request_no = models.CharField(max_length=64, blank=True, verbose_name='分账请求号')
    seller_settle_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='卖家分账金额')
    platform_commission_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='平台佣金金额')
    settlement_method = models.CharField(max_length=20, blank=True, verbose_name='结算方式')
    transfer_order_id = models.CharField(max_length=100, blank=True, verbose_name='支付宝转账订单号')

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']

    def __str__(self):
        return f"订单 #{self.id} - {self.product.title}"


class Message(models.Model):
    """消息/聊天"""
    MESSAGE_TYPES = [
        ('text', '文本'),
        ('product', '商品'),
        ('image', '图片'),
        ('recall', '撤回'),
        ('system', '系统'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name='接收者')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='messages', verbose_name='关联商品')
    content = models.TextField(verbose_name='消息内容', blank=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text', verbose_name='消息类型')
    image = models.ImageField(upload_to='messages/', null=True, blank=True, verbose_name='图片')
    payload = models.JSONField(blank=True, null=True, verbose_name='扩展数据')
    is_read = models.BooleanField(default=False, verbose_name='已读')
    recalled = models.BooleanField(default=False, verbose_name='是否撤回')
    recallable_until = models.DateTimeField(null=True, blank=True, verbose_name='可撤回截止时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='更新时间')

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
    # 支付宝收款账户（用于分账）
    alipay_login_id = models.CharField(max_length=200, blank=True, verbose_name='支付宝登录账号')
    alipay_user_id = models.CharField(max_length=30, blank=True, verbose_name='支付宝用户ID')
    alipay_real_name = models.CharField(max_length=50, blank=True, verbose_name='支付宝姓名')
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
        ('pending', '待寄出'),
        ('shipped', '已寄出'),
        ('received', '已收货'),
        ('inspected', '已检测'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recycle_orders', verbose_name='用户')
    
    # 核心关联：关联到机型模板
    template = models.ForeignKey(
        'admin_api.RecycleDeviceTemplate',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='recycle_orders',
        verbose_name='机型模板'
    )
    
    # 用户选择的具体配置（从模板的选项中选择）
    selected_storage = models.CharField(max_length=50, blank=True, verbose_name='选择的存储容量')
    selected_color = models.CharField(max_length=50, blank=True, verbose_name='选择的颜色')
    selected_ram = models.CharField(max_length=20, blank=True, verbose_name='选择的运行内存')
    selected_version = models.CharField(max_length=50, blank=True, verbose_name='选择的版本')
    
    # 保留原有字段作为快照（避免模板修改后影响历史订单）
    device_type = models.CharField(max_length=50, verbose_name='设备类型')  # 手机、平板、笔记本等
    brand = models.CharField(max_length=50, verbose_name='品牌')  # 苹果、华为、小米等
    model = models.CharField(max_length=100, verbose_name='型号')  # iPhone 13、华为Mate 60等
    storage = models.CharField(max_length=50, blank=True, verbose_name='存储容量')  # 128GB、256GB等
    
    # 问卷答案（JSON格式存储）
    questionnaire_answers = models.JSONField(default=dict, blank=True, verbose_name='问卷答案')
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
    final_price_confirmed = models.BooleanField(default=False, verbose_name='最终价已确认')
    payment_retry_count = models.IntegerField(default=0, verbose_name='打款重试次数')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    address = models.TextField(verbose_name='收货地址')
    note = models.TextField(blank=True, verbose_name='备注')
    
    # 物流信息
    shipping_carrier = models.CharField(max_length=50, blank=True, null=True, verbose_name='物流公司')
    tracking_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='运单号')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='寄出时间')
    received_at = models.DateTimeField(null=True, blank=True, verbose_name='收到时间')
    
    # 质检信息
    inspected_at = models.DateTimeField(null=True, blank=True, verbose_name='质检时间')
    
    # 打款信息
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', '待打款'),
        ('paid', '已打款'),
        ('failed', '打款失败')
    ], default='pending', verbose_name='打款状态')
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name='打款方式')
    payment_account = models.CharField(max_length=200, blank=True, null=True, verbose_name='打款账户')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='打款时间')
    payment_note = models.TextField(blank=True, null=True, verbose_name='打款备注')
    
    # 价格异议
    price_dispute = models.BooleanField(default=False, verbose_name='价格异议')
    price_dispute_reason = models.TextField(blank=True, null=True, verbose_name='价格异议原因')
    
    # 拒绝/取消原因
    reject_reason = models.TextField(blank=True, null=True, verbose_name='拒绝原因')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '回收订单'
        verbose_name_plural = '回收订单'
        ordering = ['-created_at']

    def __str__(self):
        return f"回收订单 #{self.id} - {self.brand} {self.model}"


class VerifiedDevice(models.Model):
    """
    官方验库存单品（SN 级）
    一台设备全生命周期：待处理 -> 维修/翻新中 -> 待上架 -> 在售/锁定 -> 已售出/下架
    """
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('repairing', '维修/翻新中'),
        ('ready', '待上架'),
        ('listed', '在售'),
        ('locked', '已锁定'),
        ('sold', '已售出'),
        ('removed', '已下架'),
    ]

    CONDITION_CHOICES = [
        ('new', '全新'),
        ('like_new', '99成新'),
        ('good', '95成新'),
        ('fair', '9成新'),
        ('poor', '8成新'),
    ]

    # 来源关联
    recycle_order = models.ForeignKey(RecycleOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_devices', verbose_name='来源回收单')
    
    # 机型模板关联（必填）
    template = models.ForeignKey(
        'admin_api.RecycleDeviceTemplate',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='verified_devices',
        verbose_name='机型模板'
    )
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verified_devices', verbose_name='卖家/库存持有人')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='verified_devices', verbose_name='分类')

    sn = models.CharField(max_length=100, unique=True, verbose_name='序列号/ SN')
    imei = models.CharField(max_length=100, blank=True, verbose_name='IMEI/MEID')
    
    # 具体配置（从回收订单或手动输入）
    brand = models.CharField(max_length=50, blank=True, verbose_name='品牌')
    model = models.CharField(max_length=100, blank=True, verbose_name='型号')
    storage = models.CharField(max_length=50, blank=True, verbose_name='存储容量')
    ram = models.CharField(max_length=20, blank=True, verbose_name='运行内存')
    version = models.CharField(max_length=50, blank=True, verbose_name='版本')
    color = models.CharField(max_length=50, blank=True, verbose_name='颜色')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good', verbose_name='成色')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    location = models.CharField(max_length=100, blank=True, verbose_name='仓位/存放位置')
    barcode = models.CharField(max_length=200, blank=True, verbose_name='条码/二维码内容')

    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='入库成本')
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='建议售价')

    # 媒体与质检
    cover_image = models.CharField(max_length=500, blank=True, verbose_name='封面图')
    detail_images = models.JSONField(default=list, verbose_name='详情图列表')
    inspection_reports = models.JSONField(default=list, verbose_name='质检报告列表')
    inspection_result = models.CharField(max_length=10, choices=[('pass', '合格'), ('warn', '警告'), ('fail', '不合格')], default='pass', verbose_name='质检结果')
    inspection_date = models.DateField(null=True, blank=True, verbose_name='质检日期')
    inspection_staff = models.CharField(max_length=100, blank=True, verbose_name='质检员')
    inspection_note = models.TextField(blank=True, verbose_name='质检说明')
    battery_health = models.CharField(max_length=20, blank=True, verbose_name='电池健康度')
    screen_condition = models.CharField(max_length=100, blank=True, verbose_name='屏幕情况')
    repair_history = models.TextField(blank=True, verbose_name='维修/翻新记录')

    # 与商品关联
    linked_product = models.ForeignKey('VerifiedProduct', on_delete=models.SET_NULL, null=True, blank=True, related_name='devices', verbose_name='关联商品')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '官方验库存单品'
        verbose_name_plural = '官方验库存单品'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand} {self.model} ({self.sn})"


class VerifiedProduct(models.Model):
    """官方验货商品"""
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('active', '在售'),
        ('sold', '已售出'),
        ('removed', '已下架'),
        ('draft', '草稿'),
    ]

    CONDITION_CHOICES = [
        ('new', '全新'),
        ('like_new', '99成新'),
        ('good', '95成新'),
        ('fair', '9成新'),
        ('poor', '8成新'),
    ]

    # 机型模板关联（必填）
    template = models.ForeignKey(
        'admin_api.RecycleDeviceTemplate',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='verified_products',
        verbose_name='机型模板'
    )
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verified_products', verbose_name='卖家')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='verified_products', verbose_name='分类')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    
    # 商品基本信息（从模板自动填充）
    title = models.CharField(max_length=200, verbose_name='商品标题')
    description = models.TextField(verbose_name='商品描述')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='原价')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good', verbose_name='成色')
    device_type = models.CharField(max_length=50, blank=True, verbose_name='设备类型')  # 从 template 复制
    brand = models.CharField(max_length=50, blank=True, verbose_name='品牌')  # 从 template 复制
    model = models.CharField(max_length=100, blank=True, verbose_name='型号')  # 从 template 复制
    
    # 具体配置
    storage = models.CharField(max_length=50, blank=True, verbose_name='存储容量')  # 128GB、256GB等
    ram = models.CharField(max_length=20, blank=True, verbose_name='运行内存')  # 6GB、8GB等
    version = models.CharField(max_length=50, blank=True, verbose_name='版本')  # 国行、港版等
    repair_status = models.CharField(max_length=100, blank=True, verbose_name='拆修和功能')  # 未拆未修、功能正常等
    screen_size = models.CharField(max_length=20, blank=True, verbose_name='屏幕尺寸')
    battery_health = models.CharField(max_length=20, blank=True, verbose_name='电池健康度')
    charging_type = models.CharField(max_length=50, blank=True, verbose_name='充电方式')
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name='验货时间')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_products_verified', verbose_name='验货人')
    # 新增媒体与质检字段
    cover_image = models.CharField(max_length=500, blank=True, verbose_name='封面图')
    detail_images = models.JSONField(default=list, verbose_name='详情图列表')
    inspection_reports = models.JSONField(default=list, verbose_name='质检报告列表')
    inspection_result = models.CharField(max_length=10, choices=[('pass', '合格'), ('warn', '警告'), ('fail', '不合格')], default='pass', verbose_name='质检结果')
    inspection_date = models.DateField(null=True, blank=True, verbose_name='质检日期')
    inspection_staff = models.CharField(max_length=100, blank=True, verbose_name='质检员')
    inspection_note = models.TextField(blank=True, verbose_name='质检说明')
    pricing_coefficient = models.FloatField(default=1.0, verbose_name='定价系数')
    source_tag = models.CharField(max_length=50, blank=True, default='', verbose_name='来源标签')
    stock = models.IntegerField(default=1, verbose_name='库存')
    tags = models.JSONField(default=list, verbose_name='标签')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='上架时间')
    removed_reason = models.CharField(max_length=200, blank=True, verbose_name='下架原因')
    
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
    carrier = models.CharField(max_length=50, blank=True, verbose_name='物流承运商')
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name='物流单号')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='发货时间')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='签收时间')
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


def create_verified_product_from_device(device, status='active'):
    """
    根据库存设备生成官方验商品草稿，用于库存 -> 上架打通。
    """
    if not device:
        return None

    # 已关联商品时，允许根据传入 status 强制更新状态/发布时间，避免卡在 draft
    if getattr(device, 'linked_product', None):
        product = device.linked_product
        if status and product.status != status:
            product.status = status
            updates = ['status', 'updated_at']
            if status == 'active':
                product.published_at = product.published_at or timezone.now()
                updates.append('published_at')
                device.status = 'listed'
            elif status in ['draft', 'pending', 'ready']:
                device.status = 'ready'
            product.save(update_fields=updates)
            device.save(update_fields=['status', 'updated_at'])
        return product

    template = getattr(device, 'template', None)
    if not template or (hasattr(template, 'is_active') and not template.is_active):
        raise ValueError('未关联有效的机型模板，无法生成官方验商品')

    def _norm_token(s):
        return ''.join(ch for ch in str(s or '').strip().lower() if ch.isalnum())

    def _ensure_option(value, options, field_name, allow_blank=False, aliases=None):
        """
        校验某个字段值是否在模板允许的选项中。
        - allow_blank=True：值为空时跳过校验（用于 ram/version/color 等可选字段）
        - allow_blank=False：值为空视为缺失（用于 storage 等必填字段）
        """
        normalized = str(value or '').strip()
        if not normalized:
            if allow_blank:
                return value
            raise ValueError(f'{field_name} 不能为空')
        if not options:
            return value
        option_index = {_norm_token(opt): str(opt).strip() for opt in (options or []) if str(opt).strip()}
        # 先按原值匹配（忽略大小写/空格/符号）
        hit = option_index.get(_norm_token(normalized))
        if hit:
            return hit
        # 再按别名匹配（比如 black -> 黑色）
        for a in (aliases or []):
            if not a:
                continue
            hit = option_index.get(_norm_token(a))
            if hit:
                return hit
        preview = ' / '.join(list(option_index.values())[:8])
        suffix = f'（允许：{preview}）' if preview else ''
        raise ValueError(f'{field_name} 不在模板允许的选项中{suffix}')

    storage = _ensure_option(device.storage, getattr(template, 'storages', []), '存储容量', allow_blank=False)

    # RAM / 版本 / 颜色：当模板配置了可选项时，要求必须填写且需命中选项；
    # 若模板未配置选项（或仅有空字符串等无效项），则允许留空。
    def _clean_options(raw_options):
        cleaned = []
        seen = set()
        for x in list(raw_options or []):
            s = str(x or "").strip()
            if not s:
                continue
            key = s.lower()
            if key in seen:
                continue
            cleaned.append(s)
            seen.add(key)
        return cleaned

    ram_options = _clean_options(getattr(template, 'ram_options', []) or [])
    version_options = _clean_options(getattr(template, 'version_options', []) or [])
    color_options = _clean_options(getattr(template, 'color_options', []) or [])

    # 常见别名映射：允许库存里存的是英文/简写，但模板配置的是中文时仍能命中
    color_aliases = {
        'black': ['黑色', '黑'],
        'white': ['白色', '白'],
        'silver': ['银色', '银'],
        'gold': ['金色', '金'],
        'blue': ['蓝色', '蓝'],
        'green': ['绿色', '绿'],
        'purple': ['紫色', '紫'],
        'red': ['红色', '红'],
        'pink': ['粉色', '粉'],
        'gray': ['灰色', '灰', '深空灰', '深灰'],
        'grey': ['灰色', '灰', '深空灰', '深灰'],
        'spacegray': ['深空灰', '深空灰色', '深灰'],
    }
    version_aliases = {
        'cn': ['国行'],
        'china': ['国行'],
        'guohang': ['国行'],
        'hk': ['港版'],
        'hongkong': ['港版'],
        'us': ['美版'],
        'usa': ['美版'],
        'jp': ['日版'],
        'japan': ['日版'],
    }

    ram = _ensure_option(device.ram, ram_options, '运行内存', allow_blank=(len(ram_options) == 0))
    version = _ensure_option(
        device.version,
        version_options,
        '版本',
        allow_blank=(len(version_options) == 0),
        aliases=version_aliases.get(_norm_token(device.version), [])
    )
    color = _ensure_option(
        device.color,
        color_options,
        '颜色',
        allow_blank=(len(color_options) == 0),
        aliases=color_aliases.get(_norm_token(device.color), [])
    )

    # 若命中别名/规范化，顺带回写库存设备，保证库存与模板一致
    updated_fields = []
    if storage is not None and (device.storage or '') != (storage or ''):
        device.storage = storage or ''
        updated_fields.append('storage')
    if ram is not None and (device.ram or '') != (ram or ''):
        device.ram = ram or ''
        updated_fields.append('ram')
    if version is not None and (device.version or '') != (version or ''):
        device.version = version or ''
        updated_fields.append('version')
    if color is not None and (device.color or '') != (color or ''):
        device.color = color or ''
        updated_fields.append('color')
    if updated_fields:
        updated_fields.append('updated_at')
        device.save(update_fields=updated_fields)
    title = f"{device.brand} {device.model}".strip()
    if device.storage:
        title = f"{title} {device.storage}"

    description = ''
    if template and getattr(template, 'description_template', ''):
        try:
            description = template.description_template.format(
                brand=device.brand or '',
                model=device.model or '',
                storage=device.storage or '',
                condition=device.get_condition_display() if hasattr(device, 'get_condition_display') else device.condition,
                ram=device.ram or '',
                version=device.version or ''
            )
        except Exception:
            description = f"{device.brand} {device.model} {device.storage}".strip()
    else:
        description = f"{device.brand} {device.model} {device.storage}".strip()

    cover_image = device.cover_image or (template.default_cover_image if template else '')
    detail_images = device.detail_images or (template.default_detail_images if template else [])

    price = device.suggested_price or device.cost_price or 0

    product = VerifiedProduct.objects.create(
        template=template,
        seller=device.seller,
        category=getattr(template, 'category', None),
        title=title,
        description=description,
        price=price or 0,
        original_price=None,
        condition=device.condition or 'good',
        device_type=getattr(template, 'device_type', '') if template else '',
        brand=device.brand,
        model=device.model,
        storage=storage,
        ram=ram,
        version=version,
        screen_size=getattr(template, 'screen_size', ''),
        battery_health=device.battery_health or '',
        charging_type=getattr(template, 'charging_type', ''),
        cover_image=cover_image or '',
        detail_images=detail_images,
        inspection_reports=device.inspection_reports or [],
        inspection_result=device.inspection_result or 'pass',
        inspection_date=device.inspection_date,
        inspection_staff=device.inspection_staff,
        inspection_note=device.inspection_note or '',
        pricing_coefficient=1.0,
        source_tag='official',
        stock=1,
        tags=[],
        status=status
    )

    # 生成即上架时写入发布时间，避免遗漏 publish 流程
    if status == 'active':
        product.published_at = timezone.now()
        product.save(update_fields=['published_at'])

    device.linked_product = product
    if status == 'active':
        device.status = 'listed'
    elif status in ['draft', 'pending', 'ready']:
        device.status = 'ready'
    device.save(update_fields=['linked_product', 'status', 'updated_at'])
    return product
