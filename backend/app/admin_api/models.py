from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from app.secondhand_app.models import RecycleOrder, VerifiedProduct

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
    created_at = models.DateTimeField(auto_now_add=True)

class AdminAuditQueueItem(models.Model):
    product = models.ForeignKey(VerifiedProduct, on_delete=models.CASCADE)
    type = models.CharField(max_length=32, default='new')
    rules_hit = models.JSONField(default=list)
    status = models.CharField(max_length=32, default='pending')
    decision = models.CharField(max_length=32, blank=True)
    assigned_auditor = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, blank=True)
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
