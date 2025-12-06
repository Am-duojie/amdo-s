# 回收订单数据修复脚本

## 修复订单状态问题

### 1. 检查订单状态
```sql
-- 查看所有已完成但未打款的订单
SELECT 
    id, 
    status, 
    payment_status, 
    final_price, 
    created_at,
    CASE 
        WHEN status = 'completed' AND payment_status = 'pending' AND final_price IS NOT NULL THEN '可打款'
        WHEN status = 'completed' AND payment_status = 'paid' THEN '已打款'
        WHEN status = 'completed' AND final_price IS NULL THEN '缺少最终价格'
        ELSE '状态异常'
    END as 状态说明
FROM secondhand_app_recycleorder 
WHERE status = 'completed' 
ORDER BY created_at DESC;
```

### 2. 修复订单状态
```sql
-- 修复缺少最终价格的订单（需要先进行质检）
UPDATE secondhand_app_recycleorder 
SET 
    status = 'inspected',
    inspected_at = NOW()
WHERE 
    status = 'completed' 
    AND final_price IS NULL;

-- 或者手动设置最终价格
UPDATE secondhand_app_recycleorder 
SET 
    final_price = estimated_price,
    status = 'inspected'
WHERE 
    status = 'completed' 
    AND final_price IS NULL 
    AND estimated_price IS NOT NULL;
```

### 3. 批量修复权限
```python
# 在 Django shell 中执行
from app.admin_api.models import AdminRole, AdminUser

# 给所有管理员添加打款权限
super_role = AdminRole.objects.get(name='super')
if 'inspection:payment' not in super_role.permissions:
    super_role.permissions.append('inspection:payment')
    super_role.save()
    print("已添加打款权限到超级管理员角色")

# 检查所有管理员权限
for admin in AdminUser.objects.all():
    print(f"管理员: {admin.username}, 角色: {admin.role.name}, 权限数: {len(admin.role.permissions)}")
```

### 4. 创建测试订单
```python
# 创建测试订单用于验证打款功能
from app.secondhand_app.models import RecycleOrder, User
from django.utils import timezone

# 获取测试用户
test_user = User.objects.filter(username='test_user').first()
if not test_user:
    test_user = User.objects.create_user('test_user', 'test@example.com', 'password123')

# 创建测试订单
order = RecycleOrder.objects.create(
    user=test_user,
    device_type='手机',
    brand='苹果',
    model='iPhone 13',
    storage='128GB',
    condition='good',
    estimated_price=3000.00,
    final_price=2800.00,
    status='completed',
    payment_status='pending',
    contact_name='测试用户',
    contact_phone='13800138000',
    address='测试地址'
)

print(f"创建测试订单: ID={order.id}, 状态={order.status}, 最终价格={order.final_price}")
```

### 5. 验证修复结果

访问后台管理系统，找到测试订单，验证：
1. 打款按钮是否显示
2. 点击打款按钮是否能正常操作
3. 打款后订单状态是否正确更新

## 常见问题处理

### 问题1: 打款按钮不显示
**原因**: 权限不足或订单状态不正确
**解决**: 
1. 检查管理员权限是否包含 `inspection:payment`
2. 确认订单状态为 `completed` 或 `inspected`
3. 确认订单有最终价格 (`final_price`)

### 问题2: 打款失败
**原因**: 后端校验失败
**解决**:
1. 查看浏览器控制台错误信息
2. 检查后端返回的详细错误信息
3. 确认订单状态、打款状态、最终价格

### 问题3: 重复打款
**原因**: 订单已经被标记为已打款
**解决**:
1. 检查订单的 `payment_status` 字段
2. 如果确实需要重新打款，需要先重置状态（谨慎操作）

## 预防措施

1. **完善前端验证**: 添加更详细的提示信息
2. **增强后端校验**: 提供更友好的错误信息
3. **添加操作日志**: 记录所有打款操作
4. **定期检查数据**: 确保订单状态一致性