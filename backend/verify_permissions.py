#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证管理员权限和前端权限检查
"""
import os
import sys
import django

# 设置Django环境
sys.path.append('d:/AAA/毕业设计/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.admin_api.models import AdminRole, AdminUser
import json

def verify_permissions():
    """验证管理员权限配置"""
    
    print("=== 管理员权限验证 ===")
    
    # 1. 检查超级管理员角色
    try:
        super_role = AdminRole.objects.get(name='super')
        print(f"✅ 超级管理员角色: {super_role.name}")
        print(f"   描述: {super_role.description}")
        print(f"   权限数量: {len(super_role.permissions)}")
        
        # 检查关键权限
        key_permissions = [
            'inspection:payment',
            'inspection:write', 
            'inspection:view',
            'recycled:view',
            'recycled:write',
            'payment:view',
            'payment:write',
            '*'
        ]
        
        print(f"\n关键权限检查:")
        for perm in key_permissions:
            if perm in super_role.permissions:
                print(f"   ✅ {perm}")
            else:
                print(f"   ❌ {perm}")
        
        # 显示所有权限
        print(f"\n所有权限列表:")
        for i, perm in enumerate(sorted(super_role.permissions), 1):
            print(f"   {i:2d}. {perm}")
            
    except AdminRole.DoesNotExist:
        print("❌ 未找到超级管理员角色")
        return
    
    # 2. 检查测试员角色
    try:
        test_role = AdminRole.objects.get(name='tester')
        print(f"\n✅ 测试员角色: {test_role.name}")
        print(f"   描述: {test_role.description}")
        print(f"   权限数量: {len(test_role.permissions)}")
        
        # 检查是否有打款权限
        if 'inspection:payment' in test_role.permissions:
            print(f"   ✅ 包含打款权限")
        else:
            print(f"   ❌ 缺少打款权限")
            
    except AdminRole.DoesNotExist:
        print("\n❌ 未找到测试员角色")
    
    # 3. 检查管理员用户
    print(f"\n用户检查:")
    users = [
        {'username': 'admin', 'expected_role': 'super'},
        {'username': 'test', 'expected_role': 'tester'}
    ]
    
    for user_info in users:
        try:
            user = AdminUser.objects.get(username=user_info['username'])
            role_name = user.role.name if user.role else '无角色'
            expected_role = user_info['expected_role']
            
            if role_name == expected_role:
                print(f"   ✅ {user_info['username']}: {role_name}")
            else:
                print(f"   ⚠️  {user_info['username']}: {role_name} (期望: {expected_role})")
                
            # 检查用户权限
            if user.role and 'inspection:payment' in user.role.permissions:
                print(f"      ✅ 有打款权限")
            else:
                print(f"      ❌ 无打款权限")
                
        except AdminUser.DoesNotExist:
            print(f"   ❌ {user_info['username']}: 用户不存在")
    
    # 4. 生成前端权限配置
    print(f"\n=== 前端权限配置 ===")
    print("// 在Pinia store中检查权限")
    print("const hasPerm = (code) => {")
    print("  if (!user.value) return false")
    print("  const perms = user.value.permissions || []")
    print("  if (perms.includes('*')) return true  // 通配符权限")
    print("  return perms.includes(code)")
    print("}")
    
    print(f"\n// 检查打款权限")
    print("// 在组件中使用: hasPerm('inspection:payment')")
    
    # 5. 模拟前端权限检查
    print(f"\n=== 模拟前端权限检查 ===")
    if super_role:
        mock_user = {
            'username': 'admin',
            'permissions': super_role.permissions
        }
        
        def mock_has_perm(code):
            perms = mock_user['permissions'] or []
            if '*' in perms:
                return True
            return code in perms
        
        # 测试关键权限
        test_perms = ['inspection:payment', 'inspection:write', 'random:permission']
        print(f"用户: {mock_user['username']}")
        for perm in test_perms:
            result = mock_has_perm(perm)
            print(f"   {perm}: {'✅' if result else '❌'}")

def export_permissions_config():
    """导出权限配置到JSON文件"""
    
    try:
        super_role = AdminRole.objects.get(name='super')
        test_role = AdminRole.objects.get(name='tester')
        
        config = {
            "roles": {
                "super": {
                    "name": super_role.name,
                    "description": super_role.description,
                    "permissions": sorted(super_role.permissions),
                    "permission_count": len(super_role.permissions)
                },
                "tester": {
                    "name": test_role.name,
                    "description": test_role.description,
                    "permissions": sorted(test_role.permissions),
                    "permission_count": len(test_role.permissions)
                }
            },
            "key_permissions": [
                "inspection:payment",
                "inspection:write", 
                "inspection:view",
                "payment:view",
                "payment:write",
                "*"
            ]
        }
        
        # 保存到文件
        with open('permissions_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 权限配置已导出到 permissions_config.json")
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")

if __name__ == '__main__':
    verify_permissions()
    export_permissions_config()