#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
管理员权限管理脚本 - 为admin用户添加所有权限
"""
import os
import sys
import django

# 设置Django环境
sys.path.append('d:/AAA/毕业设计/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.admin_api.models import AdminRole, AdminUser
from django.contrib.auth.hashers import make_password

def add_all_permissions():
    """为超级管理员角色添加所有可能的权限"""
    
    # 定义所有可能的权限
    all_permissions = [
        # 基础权限
        'dashboard:view',
        
        # 质检相关权限
        'inspection:view',
        'inspection:write', 
        'inspection:payment',
        'inspection:delete',
        
        # 回收订单权限
        'recycled:view',
        'recycled:write',
        'recycled:delete',
        
        # 官方验商品权限
        'verified:view',
        'verified:write',
        'verified:delete',
        
        # 审计权限
        'audit:view',
        'audit:write',
        'audit:delete',
        
        # 审计日志
        'audit_log:view',
        'audit_log:delete',
        
        # 管理员用户管理
        'admin_user:view',
        'admin_user:write',
        'admin_user:delete',
        
        # 角色管理
        'role:view',
        'role:write',
        'role:delete',
        
        # 支付相关
        'payment:view',
        'payment:write',
        'payment:delete',
        
        # 店铺管理
        'shop:view',
        'shop:write',
        'shop:delete',
        
        # 订单发货
        'order:ship',
        'order:view',
        'order:write',
        'order:delete',
        
        # 分类管理
        'category:view',
        'category:write',
        'category:delete',
        
        # 商品管理
        'product:view',
        'product:write',
        'product:delete',
        
        # 用户管理
        'user:view',
        'user:write',
        'user:delete',
        
        # 消息管理
        'message:view',
        'message:write',
        'message:delete',
        
        # 地址管理
        'address:view',
        'address:write',
        'address:delete',
        
        # 钱包管理
        'wallet:view',
        'wallet:write',
        'wallet:delete',
        
        # 系统管理
        'system:view',
        'system:write',
        'system:delete',
        
        # 通配符权限（拥有所有权限）
        '*'
    ]
    
    print("=== 开始更新管理员权限 ===")
    
    # 创建或更新超级管理员角色
    super_role, created = AdminRole.objects.get_or_create(
        name='super',
        defaults={
            'description': '拥有所有权限的超级管理员',
            'permissions': all_permissions
        }
    )
    
    if not created:
        # 更新现有角色的权限
        super_role.description = '拥有所有权限的超级管理员'
        super_role.permissions = list(set(super_role.permissions + all_permissions))
        super_role.save()
        print(f"✅ 更新超级管理员角色权限，共 {len(super_role.permissions)} 个权限")
    else:
        print(f"✅ 创建超级管理员角色，共 {len(super_role.permissions)} 个权限")
    
    # 创建或更新测试员角色（也拥有所有权限）
    test_role, created = AdminRole.objects.get_or_create(
        name='tester',
        defaults={
            'description': '测试用角色，拥有所有权限',
            'permissions': all_permissions
        }
    )
    
    if not created:
        test_role.description = '测试用角色，拥有所有权限'
        test_role.permissions = all_permissions
        test_role.save()
        print(f"✅ 更新测试员角色权限，共 {len(test_role.permissions)} 个权限")
    else:
        print(f"✅ 创建测试员角色，共 {len(test_role.permissions)} 个权限")
    
    # 更新admin用户
    try:
        admin_user = AdminUser.objects.get(username='admin')
        admin_user.role = super_role
        admin_user.email = admin_user.email or 'admin@example.com'
        admin_user.password_hash = make_password('admin')
        admin_user.save()
        print(f"✅ 更新admin用户，分配超级管理员角色")
    except AdminUser.DoesNotExist:
        # 创建新的admin用户
        admin_user = AdminUser.objects.create(
            username='admin',
            role=super_role,
            email='admin@example.com',
            password_hash=make_password('admin')
        )
        print(f"✅ 创建admin用户，分配超级管理员角色")
    
    # 创建测试用户
    try:
        test_user = AdminUser.objects.get(username='test')
        test_user.role = test_role
        test_user.email = 'test@example.com'
        test_user.password_hash = make_password('test123')
        test_user.save()
        print(f"✅ 更新test用户，分配测试员角色")
    except AdminUser.DoesNotExist:
        test_user = AdminUser.objects.create(
            username='test',
            role=test_role,
            email='test@example.com',
            password_hash=make_password('test123')
        )
        print(f"✅ 创建test用户，分配测试员角色")
    
    print(f"\n=== 权限更新完成 ===")
    print(f"管理员账号: admin / admin")
    print(f"测试员账号: test / test123")
    print(f"权限数量: {len(super_role.permissions)}")
    
    # 显示关键权限
    print(f"\n关键权限检查:")
    key_permissions = ['inspection:payment', 'inspection:write', 'inspection:view', '*']
    for perm in key_permissions:
        if perm in super_role.permissions:
            print(f"✅ {perm}")
        else:
            print(f"❌ {perm}")

if __name__ == '__main__':
    add_all_permissions()