# 数据库设计（基于 Django Models）

> 权威来源：`backend/app/secondhand_app/models.py` 与 `backend/app/admin_api/models.py`。

## 用户端业务模型（secondhand_app）

### Category

| 字段 | 类型 | 代码片段 |
|---|---|---|
| name | CharField | `name = models.CharField(max_length=50, verbose_name='分类名称')` |
| description | TextField | `description = models.TextField(blank=True, verbose_name='分类描述')` |
| type | CharField | `type = models.CharField(max_length=20, default='digital', verbose_name='分类类型')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')` |

### Shop

| 字段 | 类型 | 代码片段 |
|---|---|---|
| owner | ForeignKey | `owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops', verbose_name='店主')` |
| name | CharField | `name = models.CharField(max_length=100, verbose_name='店铺名称')` |
| description | TextField | `description = models.TextField(blank=True, verbose_name='店铺描述')` |
| logo | ImageField | `logo = models.ImageField(upload_to='shops/', null=True, blank=True, verbose_name='店铺Logo')` |
| address | CharField | `address = models.CharField(max_length=200, blank=True, verbose_name='店铺地址')` |
| contact_phone | CharField | `contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')` |
| status | CharField | `status = models.CharField(max_length=20, choices=[('active','正常'),('suspended','停用'),('closed','关闭')], default='activ...` |
| rating | DecimalField | `rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name='评分')` |
| is_verified | BooleanField | `is_verified = models.BooleanField(default=False, verbose_name='已认证')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')` |
| updated_at | DateTimeField | `updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')` |

### Product

| 字段 | 类型 | 代码片段 |
|---|---|---|
| seller | ForeignKey | `seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', verbose_name='卖家')` |
| shop | ForeignKey | `shop = models.ForeignKey('Shop', on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_n...` |
| category | ForeignKey | `category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name='分类')` |
| title | CharField | `title = models.CharField(max_length=200, verbose_name='商品标题')` |
| description | TextField | `description = models.TextField(verbose_name='商品描述')` |
| price | DecimalField | `price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')` |
| original_price | DecimalField | `original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='原价')` |
| condition | CharField | `condition = models.CharField(max_length=20, choices=[` |
| status | CharField | `status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')` |
| location | CharField | `location = models.CharField(max_length=100, verbose_name='所在地')` |
| contact_phone | CharField | `contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')` |
| contact_wechat | CharField | `contact_wechat = models.CharField(max_length=50, blank=True, verbose_name='微信')` |
| view_count | IntegerField | `view_count = models.IntegerField(default=0, verbose_name='浏览次数')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')` |
| updated_at | DateTimeField | `updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')` |

### ProductImage

| 字段 | 类型 | 代码片段 |
|---|---|---|
| product | ForeignKey | `product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='商品')` |
| image | ImageField | `image = models.ImageField(upload_to='products/', verbose_name='图片')` |
| is_primary | BooleanField | `is_primary = models.BooleanField(default=False, verbose_name='主图')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')` |

### Order

| 字段 | 类型 | 代码片段 |
|---|---|---|
| buyer | ForeignKey | `buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='买家')` |
| product | ForeignKey | `product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders', verbose_name='商品')` |
| total_price | DecimalField | `total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总价')` |
| status | CharField | `status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')` |
| shipping_address | TextField | `shipping_address = models.TextField(verbose_name='收货地址')` |
| shipping_name | CharField | `shipping_name = models.CharField(max_length=50, verbose_name='收货人姓名')` |
| shipping_phone | CharField | `shipping_phone = models.CharField(max_length=20, verbose_name='收货人电话')` |
| carrier | CharField | `carrier = models.CharField(max_length=50, blank=True, verbose_name='物流承运商')` |
| tracking_number | CharField | `tracking_number = models.CharField(max_length=100, blank=True, verbose_name='物流单号')` |
| shipped_at | DateTimeField | `shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='发货时间')` |
| delivered_at | DateTimeField | `delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='签收时间')` |
| note | TextField | `note = models.TextField(blank=True, verbose_name='备注')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')` |
| updated_at | DateTimeField | `updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')` |
| alipay_trade_no | CharField | `alipay_trade_no = models.CharField(max_length=64, blank=True, verbose_name='支付宝交易号')` |
| settlement_status | CharField | `settlement_status = models.CharField(max_length=20, choices=[('pending','待分账'),('settled','已分账'),('failed','分账失败')], ...` |
| settled_at | DateTimeField | `settled_at = models.DateTimeField(null=True, blank=True, verbose_name='分账时间')` |
| settle_request_no | CharField | `settle_request_no = models.CharField(max_length=64, blank=True, verbose_name='分账请求号')` |
| seller_settle_amount | DecimalField | `seller_settle_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='卖家分账...` |
| platform_commission_amount | DecimalField | `platform_commission_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name...` |
| settlement_method | CharField | `settlement_method = models.CharField(max_length=20, blank=True, verbose_name='结算方式')` |
| transfer_order_id | CharField | `transfer_order_id = models.CharField(max_length=100, blank=True, verbose_name='支付宝转账订单号')` |

### Message

| 字段 | 类型 | 代码片段 |
|---|---|---|
| sender | ForeignKey | `sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')` |
| receiver | ForeignKey | `receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name='接收者')` |
| product | ForeignKey | `product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='messages', verbos...` |
| content | TextField | `content = models.TextField(verbose_name='消息内容', blank=True)` |
| message_type | CharField | `message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text', verbose_name='消息类型')` |
| image | ImageField | `image = models.ImageField(upload_to='messages/', null=True, blank=True, verbose_name='图片')` |
| payload | JSONField | `payload = models.JSONField(blank=True, null=True, verbose_name='扩展数据')` |
| is_read | BooleanField | `is_read = models.BooleanField(default=False, verbose_name='已读')` |
| recalled | BooleanField | `recalled = models.BooleanField(default=False, verbose_name='是否撤回')` |
| recallable_until | DateTimeField | `recallable_until = models.DateTimeField(null=True, blank=True, verbose_name='可撤回截止时间')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')` |
| updated_at | DateTimeField | `updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='更新时间')` |

### Favorite

| 字段 | 类型 | 代码片段 |
|---|---|---|
| user | ForeignKey | `user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='用户')` |
| product | ForeignKey | `product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites', verbose_name='商品')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')` |

### Address

| 字段 | 类型 | 代码片段 |
|---|---|---|
| user | ForeignKey | `user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')` |
| name | CharField | `name = models.CharField(max_length=50, verbose_name='收货人姓名')` |
| phone | CharField | `phone = models.CharField(max_length=20, verbose_name='收货人电话')` |
| province | CharField | `province = models.CharField(max_length=50, verbose_name='省')` |
| city | CharField | `city = models.CharField(max_length=50, verbose_name='市')` |
| district | CharField | `district = models.CharField(max_length=50, verbose_name='区/县')` |
| detail_address | TextField | `detail_address = models.TextField(verbose_name='详细地址')` |
| is_default | BooleanField | `is_default = models.BooleanField(default=False, verbose_name='是否默认')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')` |
| updated_at | DateTimeField | `updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')` |

### UserProfile

| 字段 | 类型 | 代码片段 |
|---|---|---|
| user | OneToOneField | `user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')` |
| avatar | ImageField | `avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')` |
| bio | TextField | `bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')` |
| location | CharField | `location = models.CharField(max_length=100, blank=True, verbose_name='所在地')` |
| alipay_login_id | CharField | `alipay_login_id = models.CharField(max_length=200, blank=True, verbose_name='支付宝登录账号')` |
| alipay_user_id | CharField | `alipay_user_id = models.CharField(max_length=30, blank=True, verbose_name='支付宝用户ID')` |
| alipay_real_name | CharField | `alipay_real_name = models.CharField(max_length=50, blank=True, verbose_name='支付宝姓名')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')` |
| updated_at | DateTimeField | `updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')` |

### Wallet

| 字段 | 类型 | 代码片段 |
|---|---|---|
| user | OneToOneField | `user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet', verbose_name='用户')` |
| balance | DecimalField | `balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='余额')` |
| frozen_balance | DecimalField | `frozen_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='冻结余额')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')` |
| updated_at | DateTimeField | `updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')` |

### WalletTransaction

| 字段 | 类型 | 代码片段 |
|---|---|---|
| wallet | ForeignKey | `wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions', verbose_name='钱包')` |
| transaction_type | CharField | `transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name='交易类型')` |
| amount | DecimalField | `amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='金额')` |
| balance_after | DecimalField | `balance_after = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='交易后余额')` |
| related_order | ForeignKey | `related_order = models.ForeignKey('RecycleOrder', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联回...` |
| related_market_order | ForeignKey | `related_market_order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联交...` |
| note | TextField | `note = models.TextField(blank=True, verbose_name='备注')` |
| withdraw_status | CharField | `withdraw_status = models.CharField(max_length=20, choices=WITHDRAW_STATUS, null=True, blank=True, verbose_name='提现状态')` |
| alipay_account | CharField | `alipay_account = models.CharField(max_length=200, blank=True, verbose_name='支付宝账号')` |
| alipay_name | CharField | `alipay_name = models.CharField(max_length=50, blank=True, verbose_name='支付宝姓名')` |
| alipay_order_id | CharField | `alipay_order_id = models.CharField(max_length=100, blank=True, verbose_name='支付宝订单号')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')` |

### RecycleOrder

| 字段 | 类型 | 代码片段 |
|---|---|---|
| user | ForeignKey | `user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recycle_orders', verbose_name='用户')` |
| device_type | CharField | `device_type = models.CharField(max_length=50, verbose_name='设备类型')  # 手机、平板、笔记本等` |
| brand | CharField | `brand = models.CharField(max_length=50, verbose_name='品牌')  # 苹果、华为、小米等` |
| model | CharField | `model = models.CharField(max_length=100, verbose_name='型号')  # iPhone 13、华为Mate 60等` |
| storage | CharField | `storage = models.CharField(max_length=50, blank=True, verbose_name='存储容量')  # 128GB、256GB等` |
| condition | CharField | `condition = models.CharField(max_length=20, choices=[` |
| estimated_price | DecimalField | `estimated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='预估价格')` |
| final_price | DecimalField | `final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='最终价格')` |
| bonus | DecimalField | `bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='加价')` |
| final_price_confirmed | BooleanField | `final_price_confirmed = models.BooleanField(default=False, verbose_name='最终价已确认')` |
| payment_retry_count | IntegerField | `payment_retry_count = models.IntegerField(default=0, verbose_name='打款重试次数')` |
| status | CharField | `status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')` |
| contact_name | CharField | `contact_name = models.CharField(max_length=50, verbose_name='联系人姓名')` |
| contact_phone | CharField | `contact_phone = models.CharField(max_length=20, verbose_name='联系电话')` |
| address | TextField | `address = models.TextField(verbose_name='收货地址')` |
| note | TextField | `note = models.TextField(blank=True, verbose_name='备注')` |
| shipping_carrier | CharField | `shipping_carrier = models.CharField(max_length=50, blank=True, null=True, verbose_name='物流公司')` |
| tracking_number | CharField | `tracking_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='运单号')` |
| shipped_at | DateTimeField | `shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='寄出时间')` |
| received_at | DateTimeField | `received_at = models.DateTimeField(null=True, blank=True, verbose_name='收到时间')` |
| inspected_at | DateTimeField | `inspected_at = models.DateTimeField(null=True, blank=True, verbose_name='质检时间')` |
| payment_status | CharField | `payment_status = models.CharField(max_length=20, choices=[` |
| payment_method | CharField | `payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name='打款方式')` |
| payment_account | CharField | `payment_account = models.CharField(max_length=200, blank=True, null=True, verbose_name='打款账户')` |
| paid_at | DateTimeField | `paid_at = models.DateTimeField(null=True, blank=True, verbose_name='打款时间')` |
| payment_note | TextField | `payment_note = models.TextField(blank=True, null=True, verbose_name='打款备注')` |
| price_dispute | BooleanField | `price_dispute = models.BooleanField(default=False, verbose_name='价格异议')` |
| price_dispute_reason | TextField | `price_dispute_reason = models.TextField(blank=True, null=True, verbose_name='价格异议原因')` |
| reject_reason | TextField | `reject_reason = models.TextField(blank=True, null=True, verbose_name='拒绝原因')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')` |
| updated_at | DateTimeField | `updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')` |

### VerifiedDevice

| 字段 | 类型 | 代码片段 |
|---|---|---|
| recycle_order | ForeignKey | `recycle_order = models.ForeignKey(RecycleOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='verif...` |
| seller | ForeignKey | `seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verified_devices', verbose_name='卖家/库存持有人')` |
| category | ForeignKey | `category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='verified_devices', verbose...` |
| sn | CharField | `sn = models.CharField(max_length=100, unique=True, verbose_name='序列号/ SN')` |
| imei | CharField | `imei = models.CharField(max_length=100, blank=True, verbose_name='IMEI/MEID')` |
| brand | CharField | `brand = models.CharField(max_length=50, blank=True, verbose_name='品牌')` |
| model | CharField | `model = models.CharField(max_length=100, blank=True, verbose_name='型号')` |
| storage | CharField | `storage = models.CharField(max_length=50, blank=True, verbose_name='存储容量')` |
| condition | CharField | `condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good', verbose_name='成色')` |
| status | CharField | `status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')` |
| location | CharField | `location = models.CharField(max_length=100, blank=True, verbose_name='仓位/存放位置')` |
| barcode | CharField | `barcode = models.CharField(max_length=200, blank=True, verbose_name='条码/二维码内容')` |
| cost_price | DecimalField | `cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='入库成本')` |
| suggested_price | DecimalField | `suggested_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='建议售价')` |
| cover_image | CharField | `cover_image = models.CharField(max_length=500, blank=True, verbose_name='封面图')` |
| detail_images | JSONField | `detail_images = models.JSONField(default=list, verbose_name='详情图列表')` |
| inspection_reports | JSONField | `inspection_reports = models.JSONField(default=list, verbose_name='质检报告列表')` |
| inspection_result | CharField | `inspection_result = models.CharField(max_length=10, choices=[('pass', '合格'), ('warn', '警告'), ('fail', '不合格')], defaul...` |
| inspection_date | DateField | `inspection_date = models.DateField(null=True, blank=True, verbose_name='质检日期')` |
| inspection_staff | CharField | `inspection_staff = models.CharField(max_length=100, blank=True, verbose_name='质检员')` |
| inspection_note | TextField | `inspection_note = models.TextField(blank=True, verbose_name='质检说明')` |
| battery_health | CharField | `battery_health = models.CharField(max_length=20, blank=True, verbose_name='电池健康度')` |
| screen_condition | CharField | `screen_condition = models.CharField(max_length=100, blank=True, verbose_name='屏幕情况')` |
| repair_history | TextField | `repair_history = models.TextField(blank=True, verbose_name='维修/翻新记录')` |
| linked_product | ForeignKey | `linked_product = models.ForeignKey('VerifiedProduct', on_delete=models.SET_NULL, null=True, blank=True, related_name=...` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')` |
| updated_at | DateTimeField | `updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')` |

### VerifiedProduct

| 字段 | 类型 | 代码片段 |
|---|---|---|
| seller | ForeignKey | `seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verified_products', verbose_name='卖家')` |
| shop | ForeignKey | `shop = models.ForeignKey('Shop', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_products', ...` |
| category | ForeignKey | `category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='verified_products', verbos...` |
| title | CharField | `title = models.CharField(max_length=200, verbose_name='商品标题')` |
| description | TextField | `description = models.TextField(verbose_name='商品描述')` |
| price | DecimalField | `price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')` |
| original_price | DecimalField | `original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='原价')` |
| condition | CharField | `condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good', verbose_name='成色')` |
| status | CharField | `status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')` |
| location | CharField | `location = models.CharField(max_length=100, verbose_name='所在地')` |
| contact_phone | CharField | `contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')` |
| contact_wechat | CharField | `contact_wechat = models.CharField(max_length=50, blank=True, verbose_name='微信')` |
| brand | CharField | `brand = models.CharField(max_length=50, blank=True, verbose_name='品牌')  # 苹果、华为、小米等` |
| model | CharField | `model = models.CharField(max_length=100, blank=True, verbose_name='型号')  # iPhone 13、华为Mate 60等` |
| storage | CharField | `storage = models.CharField(max_length=50, blank=True, verbose_name='存储容量')  # 128GB、256GB等` |
| screen_size | CharField | `screen_size = models.CharField(max_length=20, blank=True, verbose_name='屏幕尺寸')` |
| battery_health | CharField | `battery_health = models.CharField(max_length=20, blank=True, verbose_name='电池健康度')` |
| charging_type | CharField | `charging_type = models.CharField(max_length=50, blank=True, verbose_name='充电方式')` |
| verified_at | DateTimeField | `verified_at = models.DateTimeField(null=True, blank=True, verbose_name='验货时间')` |
| verified_by | ForeignKey | `verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_produc...` |
| cover_image | CharField | `cover_image = models.CharField(max_length=500, blank=True, verbose_name='封面图')` |
| detail_images | JSONField | `detail_images = models.JSONField(default=list, verbose_name='详情图列表')` |
| inspection_reports | JSONField | `inspection_reports = models.JSONField(default=list, verbose_name='质检报告列表')` |
| inspection_result | CharField | `inspection_result = models.CharField(max_length=10, choices=[('pass', '合格'), ('warn', '警告'), ('fail', '不合格')], defaul...` |
| inspection_date | DateField | `inspection_date = models.DateField(null=True, blank=True, verbose_name='质检日期')` |
| inspection_staff | CharField | `inspection_staff = models.CharField(max_length=100, blank=True, verbose_name='质检员')` |
| inspection_note | TextField | `inspection_note = models.TextField(blank=True, verbose_name='质检说明')` |
| stock | IntegerField | `stock = models.IntegerField(default=1, verbose_name='库存')` |
| tags | JSONField | `tags = models.JSONField(default=list, verbose_name='标签')` |
| published_at | DateTimeField | `published_at = models.DateTimeField(null=True, blank=True, verbose_name='上架时间')` |
| removed_reason | CharField | `removed_reason = models.CharField(max_length=200, blank=True, verbose_name='下架原因')` |
| view_count | IntegerField | `view_count = models.IntegerField(default=0, verbose_name='浏览次数')` |
| sales_count | IntegerField | `sales_count = models.IntegerField(default=0, verbose_name='销量')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')` |
| updated_at | DateTimeField | `updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')` |

### VerifiedProductImage

| 字段 | 类型 | 代码片段 |
|---|---|---|
| product | ForeignKey | `product = models.ForeignKey(VerifiedProduct, on_delete=models.CASCADE, related_name='images', verbose_name='商品')` |
| image | ImageField | `image = models.ImageField(upload_to='verified_products/', verbose_name='图片')` |
| is_primary | BooleanField | `is_primary = models.BooleanField(default=False, verbose_name='主图')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')` |

### VerifiedOrder

| 字段 | 类型 | 代码片段 |
|---|---|---|
| buyer | ForeignKey | `buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verified_orders', verbose_name='买家')` |
| product | ForeignKey | `product = models.ForeignKey(VerifiedProduct, on_delete=models.CASCADE, related_name='orders', verbose_name='商品')` |
| total_price | DecimalField | `total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总价')` |
| status | CharField | `status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')` |
| shipping_address | TextField | `shipping_address = models.TextField(verbose_name='收货地址')` |
| shipping_name | CharField | `shipping_name = models.CharField(max_length=50, verbose_name='收货人姓名')` |
| shipping_phone | CharField | `shipping_phone = models.CharField(max_length=20, verbose_name='收货人电话')` |
| carrier | CharField | `carrier = models.CharField(max_length=50, blank=True, verbose_name='物流承运商')` |
| tracking_number | CharField | `tracking_number = models.CharField(max_length=100, blank=True, verbose_name='物流单号')` |
| shipped_at | DateTimeField | `shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='发货时间')` |
| delivered_at | DateTimeField | `delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='签收时间')` |
| note | TextField | `note = models.TextField(blank=True, verbose_name='备注')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')` |
| updated_at | DateTimeField | `updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')` |

### VerifiedFavorite

| 字段 | 类型 | 代码片段 |
|---|---|---|
| user | ForeignKey | `user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verified_favorites', verbose_name='用户')` |
| product | ForeignKey | `product = models.ForeignKey(VerifiedProduct, on_delete=models.CASCADE, related_name='favorites', verbose_name='商品')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')` |

## 管理端模型（admin_api）

### AdminRole

| 字段 | 类型 | 代码片段 |
|---|---|---|
| name | CharField | `name = models.CharField(max_length=32, unique=True)` |
| description | CharField | `description = models.CharField(max_length=128, blank=True)` |
| permissions | JSONField | `permissions = models.JSONField(default=list)` |

### AdminUser

| 字段 | 类型 | 代码片段 |
|---|---|---|
| username | CharField | `username = models.CharField(max_length=64, unique=True)` |
| role | ForeignKey | `role = models.ForeignKey(AdminRole, on_delete=models.SET_NULL, null=True)` |
| email | EmailField | `email = models.EmailField(blank=True)` |
| password_hash | CharField | `password_hash = models.CharField(max_length=128, blank=True)` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True)` |

### AdminSession

| 字段 | 类型 | 代码片段 |
|---|---|---|
| token | CharField | `token = models.CharField(max_length=128, unique=True)` |
| user | ForeignKey | `user = models.ForeignKey(AdminUser, on_delete=models.CASCADE)` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True)` |
| expires_at | DateTimeField | `expires_at = models.DateTimeField(null=True, blank=True)` |

### AdminInspectionReport

| 字段 | 类型 | 代码片段 |
|---|---|---|
| order | ForeignKey | `order = models.ForeignKey(RecycleOrder, on_delete=models.CASCADE, related_name='admin_reports')` |
| check_items | JSONField | `check_items = models.JSONField(default=dict)` |
| remarks | TextField | `remarks = models.TextField(blank=True)` |
| evidence | JSONField | `evidence = models.JSONField(default=list)` |
| overall_result | CharField | `overall_result = models.CharField(max_length=32, default='passed')` |
| recommend_price | DecimalField | `recommend_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)` |
| score | DecimalField | `score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)` |
| template_name | CharField | `template_name = models.CharField(max_length=64, default='default')` |
| template_version | CharField | `template_version = models.CharField(max_length=32, default='v1')` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True)` |

### AdminAuditQueueItem

| 字段 | 类型 | 代码片段 |
|---|---|---|
| product | ForeignKey | `product = models.ForeignKey(VerifiedProduct, on_delete=models.CASCADE)` |
| type | CharField | `type = models.CharField(max_length=32, default='new')` |
| rules_hit | JSONField | `rules_hit = models.JSONField(default=list)` |
| status | CharField | `status = models.CharField(max_length=32, default='pending')` |
| decision | CharField | `decision = models.CharField(max_length=32, blank=True)` |
| assigned_auditor | ForeignKey | `assigned_auditor = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, blank=True)` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True)` |

### AdminAuditLog

| 字段 | 类型 | 代码片段 |
|---|---|---|
| actor | ForeignKey | `actor = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True)` |
| target_type | CharField | `target_type = models.CharField(max_length=64)` |
| target_id | IntegerField | `target_id = models.IntegerField()` |
| action | CharField | `action = models.CharField(max_length=64)` |
| snapshot_json | JSONField | `snapshot_json = models.JSONField(default=dict)` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True)` |

### AdminRefreshToken

| 字段 | 类型 | 代码片段 |
|---|---|---|
| user | ForeignKey | `user = models.ForeignKey(AdminUser, on_delete=models.CASCADE)` |
| token | CharField | `token = models.CharField(max_length=128, unique=True)` |
| expires_at | DateTimeField | `expires_at = models.DateTimeField()` |
| revoked | BooleanField | `revoked = models.BooleanField(default=False)` |
| created_at | DateTimeField | `created_at = models.DateTimeField(auto_now_add=True)` |

### AdminTokenBlacklist

| 字段 | 类型 | 代码片段 |
|---|---|---|
| jti | CharField | `jti = models.CharField(max_length=64, unique=True)` |
| blacklisted_at | DateTimeField | `blacklisted_at = models.DateTimeField(auto_now_add=True)` |
