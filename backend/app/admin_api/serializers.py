from rest_framework import serializers
from .models import AdminUser, AdminRole, AdminInspectionReport, AdminAuditQueueItem
from app.secondhand_app.models import RecycleOrder, VerifiedProduct, Shop

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
    class Meta:
        model = VerifiedProduct
        fields = ['id','title','condition','price','status']

class AdminAuditQueueItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAuditQueueItem
        fields = ['id','type','rules_hit','status','decision']

class ShopAdminSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username')
    class Meta:
        model = Shop
        fields = ['id','name','owner','status','rating','is_verified','created_at']
