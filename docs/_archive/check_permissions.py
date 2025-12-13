#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证管理员权限脚本
"""
import os
import sys
import django

# 设置Django环境
sys.path.append('d:/AAA/毕业设计/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from app.admin_api.models import AdminRole, AdminUser

def check_admin_permissions():
    """检查管理员权限"""
    print("=== 管理员权限检查 ===")
    
    # 检查超级管理员角色
    try:
        super_role = AdminRole.objects.get(name='super')
        print(f"超级管理员角色: {super_role.name}")
        print(f"权限列表: {super_role.permissions}")
        
        # 检查是否有inspection:payment权限
        if 'inspection:payment' in super_role.permissions:
            print("✅ 已找到 inspection:payment 权限")
        else:
            print("❌ 未找到 inspection:payment 权限")
            
        # 显示所有权限
        print("\n详细权限列表:")
        for perm in sorted(super_role.permissions):
            print(f"  - {perm}")
            
    except AdminRole.DoesNotExist:
        print("❌ 未找到超级管理员角色")
    
    # 检查管理员用户
    try:
        admin_user = AdminUser.objects.get(username='admin')
        print(f"\n管理员用户: {admin_user.username}")
        print(f"角色: {admin_user.role.name if admin_user.role else '无角色'}")
        
        if admin_user.role:
            print(f"权限数量: {len(admin_user.role.permissions)}")
            
    except AdminUser.DoesNotExist:
        print("❌ 未找到admin用户")
    
    print("\n=== 检查完成 ===")

if __name__ == '__main__':
    check_admin_permissions()