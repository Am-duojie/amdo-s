from rest_framework import serializers
from .models import (
    AdminUser, AdminRole, AdminInspectionReport, AdminAuditQueueItem,
    RecycleDeviceTemplate, RecycleQuestionTemplate, RecycleQuestionOption
)
from app.secondhand_app.models import RecycleOrder, VerifiedProduct, VerifiedDevice

class AdminUserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.name', allow_null=True)
    permissions = serializers.ListField(source='role.permissions', child=serializers.CharField(), allow_null=True)
    class Meta:
        model = AdminUser
        fields = ['id','username','email','role','permissions']

class RecycleOrderListSerializer(serializers.ModelSerializer):
    device = serializers.SerializerMethodField()
    class Meta:
        model = RecycleOrder
        fields = ['id','status','device','created_at']
    def get_device(self, obj):
        return f"{obj.brand} {obj.model}"

class VerifiedProductListSerializer(serializers.ModelSerializer):
    linked_device_id = serializers.SerializerMethodField()
    linked_device_sn = serializers.SerializerMethodField()
    class Meta:
        model = VerifiedProduct
        fields = [
            'id', 'title', 'condition', 'price', 'original_price', 'status', 'stock',
            'cover_image', 'sales_count', 'created_at', 'tags',
            'linked_device_id', 'linked_device_sn'
        ]

    def get_linked_device_id(self, obj):
        try:
            dev = getattr(obj, 'devices', None)
            dev = dev.first() if dev is not None else None
            return getattr(dev, 'id', None)
        except Exception:
            return None

    def get_linked_device_sn(self, obj):
        try:
            dev = getattr(obj, 'devices', None)
            dev = dev.first() if dev is not None else None
            return getattr(dev, 'sn', None)
        except Exception:
            return None


class VerifiedDeviceListSerializer(serializers.ModelSerializer):
    linked_product_id = serializers.IntegerField(source='linked_product.id', read_only=True)
    template_id = serializers.IntegerField(source='template.id', read_only=True)

    class Meta:
        model = VerifiedDevice
        fields = [
            'id', 'sn', 'imei', 'brand', 'model', 'storage', 'ram', 'version', 'color',
            'condition', 'status', 'cover_image', 'detail_images', 'listing_description',
            'location', 'suggested_price',
            'inspection_reports', 'inspection_note', 'template_id', 'created_at', 'linked_product_id'
        ]


class OfficialInventorySerializer(serializers.ModelSerializer):
    template_id = serializers.IntegerField(source='template.id', read_only=True)
    template_name = serializers.CharField(source='template.model', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    linked_product_id = serializers.IntegerField(source='linked_product.id', read_only=True)

    class Meta:
        model = VerifiedDevice
        fields = [
            'id', 'sn', 'imei', 'brand', 'model', 'storage', 'ram', 'version', 'color',
            'condition', 'status', 'location', 'suggested_price', 'cost_price',
            'inspection_result', 'inspection_date', 'inspection_staff',
            'template_id', 'template_name', 'category_name', 'linked_product_id',
            'created_at', 'updated_at'
        ]

class AdminAuditQueueItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAuditQueueItem
        fields = ['id','type','rules_hit','status','decision']

# ==================== 回收机型模板序列化器 ====================

class RecycleQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecycleQuestionOption
        fields = ['id', 'question_template', 'value', 'label', 'desc', 'impact', 'option_order', 'is_active', 'created_at', 'updated_at']
        extra_kwargs = {
            'question_template': {'write_only': True, 'required': False}
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态设置 queryset，避免循环导入
        if 'question_template' in self.fields:
            from .models import RecycleQuestionTemplate
            self.fields['question_template'].queryset = RecycleQuestionTemplate.objects.all()


class RecycleQuestionTemplateSerializer(serializers.ModelSerializer):
    options = RecycleQuestionOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = RecycleQuestionTemplate
        fields = [
            'id', 'device_template', 'step_order', 'key', 'title', 'helper', 'question_type',
            'is_required', 'is_active', 'options', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'device_template': {'write_only': True, 'required': False}
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态设置 queryset，避免循环导入
        if 'device_template' in self.fields:
            from .models import RecycleDeviceTemplate
            self.fields['device_template'].queryset = RecycleDeviceTemplate.objects.all()


class RecycleDeviceTemplateSerializer(serializers.ModelSerializer):
    questions = RecycleQuestionTemplateSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    
    class Meta:
        model = RecycleDeviceTemplate
        fields = [
            'id', 'device_type', 'brand', 'model', 'storages', 'base_prices', 'series',
            'ram_options', 'version_options', 'color_options',
            'default_cover_image', 'default_detail_images', 'description_template',
            'category', 'category_name',
            'is_active', 'created_by', 'created_by_username', 'questions',
            'created_at', 'updated_at'
        ]


class RecycleDeviceTemplateListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    
    class Meta:
        model = RecycleDeviceTemplate
        fields = [
            'id', 'device_type', 'brand', 'model', 'storages', 'base_prices', 'series',
            'ram_options', 'version_options', 'color_options',
            'default_cover_image', 'category_name',
            'is_active', 'created_by_username', 'question_count',
            'created_at', 'updated_at'
        ]
    
    def get_question_count(self, obj):
        return obj.questions.filter(is_active=True).count()
