from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from app.secondhand_app.models import RecycleOrder

class AdminRole(models.Model):
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=128, blank=True)
    permissions = models.JSONField(default=list)

class AdminUser(models.Model):
    username = models.CharField(max_length=64, unique=True)
    role = models.ForeignKey(AdminRole, on_delete=models.SET_NULL, null=True)
    email = models.EmailField(blank=True)
    password_hash = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AdminSession(models.Model):
    token = models.CharField(max_length=128, unique=True)
    user = models.ForeignKey(AdminUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

class AdminInspectionReport(models.Model):
    order = models.ForeignKey(RecycleOrder, on_delete=models.CASCADE, related_name='admin_reports')
    check_items = models.JSONField(default=dict)
    remarks = models.TextField(blank=True)
    evidence = models.JSONField(default=list)
    overall_result = models.CharField(max_length=32, default='passed')
    recommend_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    template_name = models.CharField(max_length=64, default='default')
    template_version = models.CharField(max_length=32, default='v1')
    created_at = models.DateTimeField(auto_now_add=True)

class AdminAuditLog(models.Model):
    actor = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True)
    target_type = models.CharField(max_length=64)
    target_id = models.IntegerField()
    action = models.CharField(max_length=64)
    snapshot_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class AdminRefreshToken(models.Model):
    user = models.ForeignKey(AdminUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=128, unique=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class AdminTokenBlacklist(models.Model):
    jti = models.CharField(max_length=64, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)


# ==================== 回收机型模板管理 ====================

class RecycleDeviceTemplate(models.Model):
    """回收机型模板"""
    device_type = models.CharField(max_length=32, verbose_name='设备类型', help_text='如：手机、平板、笔记本')
    brand = models.CharField(max_length=64, verbose_name='品牌')
    model = models.CharField(max_length=128, verbose_name='型号')
    storages = models.JSONField(default=list, verbose_name='存储容量列表', help_text='如：["128GB", "256GB", "512GB"]')
    base_prices = models.JSONField(
        default=dict, 
        verbose_name='基础价格表', 
        help_text='按存储容量存储基础价格，格式：{"128GB": 4500, "256GB": 5200, "512GB": 6500}，单位为元'
    )
    series = models.CharField(max_length=64, blank=True, verbose_name='系列', help_text='如：iPhone 13系列')
    
    # 规格选项（用于前端展示和官方验商品）
    ram_options = models.JSONField(default=list, blank=True, verbose_name='运行内存选项', help_text='如：["6GB", "8GB", "12GB"]')
    version_options = models.JSONField(default=list, blank=True, verbose_name='版本选项', help_text='如：["国行", "港版", "美版"]')
    color_options = models.JSONField(default=list, blank=True, verbose_name='颜色选项', help_text='如：["黑色", "白色", "蓝色"]')
    
    # 默认图片（用于官方验商品）
    default_cover_image = models.CharField(max_length=500, blank=True, verbose_name='默认封面图')
    default_detail_images = models.JSONField(default=list, blank=True, verbose_name='默认详情图列表')
    
    # 商品描述模板
    description_template = models.TextField(blank=True, verbose_name='商品描述模板', help_text='支持变量：{brand} {model} {storage} {condition} {ram} {version}')
    
    # 分类关联
    category = models.ForeignKey('secondhand_app.Category', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='商品分类')
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_by = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '回收机型模板'
        verbose_name_plural = '回收机型模板'
        unique_together = [['device_type', 'brand', 'model']]
        ordering = ['device_type', 'brand', 'model']

    def __str__(self):
        return f"{self.device_type} / {self.brand} / {self.model}"


class RecycleQuestionTemplate(models.Model):
    """回收问卷步骤模板"""
    device_template = models.ForeignKey(
        RecycleDeviceTemplate,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='机型模板'
    )
    step_order = models.IntegerField(verbose_name='步骤顺序', help_text='从1开始')
    key = models.CharField(max_length=64, verbose_name='问题标识', help_text='如：channel, color, storage')
    title = models.CharField(max_length=128, verbose_name='问题标题')
    helper = models.CharField(max_length=256, blank=True, verbose_name='提示文本')
    question_type = models.CharField(
        max_length=16,
        choices=[('single', '单选'), ('multi', '多选')],
        default='single',
        verbose_name='问题类型'
    )
    is_required = models.BooleanField(default=True, verbose_name='是否必填')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '问卷步骤模板'
        verbose_name_plural = '问卷步骤模板'
        unique_together = [['device_template', 'step_order'], ['device_template', 'key']]
        ordering = ['device_template', 'step_order']

    def __str__(self):
        return f"{self.device_template} - {self.step_order}. {self.title}"


class RecycleQuestionOption(models.Model):
    """回收问卷选项"""
    question_template = models.ForeignKey(
        RecycleQuestionTemplate,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name='问题模板'
    )
    value = models.CharField(max_length=128, verbose_name='选项值', help_text='如：official, black, 256GB')
    label = models.CharField(max_length=128, verbose_name='选项标签', help_text='显示给用户的文本')
    desc = models.CharField(max_length=256, blank=True, verbose_name='选项描述', help_text='辅助说明文本')
    impact = models.CharField(
        max_length=16,
        choices=[
            ('positive', '正面影响'),
            ('minor', '轻微影响'),
            ('major', '重大影响'),
            ('critical', '严重影响'),
        ],
        blank=True,
        verbose_name='对估价的影响'
    )
    option_order = models.IntegerField(default=0, verbose_name='选项顺序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '问卷选项'
        verbose_name_plural = '问卷选项'
        unique_together = [['question_template', 'value']]
        ordering = ['question_template', 'option_order', 'id']

    def __str__(self):
        return f"{self.question_template.title} - {self.label}"
