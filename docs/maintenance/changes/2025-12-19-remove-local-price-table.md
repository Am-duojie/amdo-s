# 2025-12-19 - 移除本地价目表（以数据库模板为准）

## 变更内容

- 删除回收业务的本地价目表常量（`DEFAULT_LOCAL_PRICE_TABLE` / `LOCAL_PRICE_TABLE`）。
- 回收目录与估价不再回退到代码内价目表，统一以数据库机型模板为准：
  - 机型模板：`admin_api.RecycleDeviceTemplate`
  - 基础价格：`admin_api.RecycleDeviceTemplate.base_prices`

## 影响范围

- `backend/app/secondhand_app/price_service.py`：本地估价改为读取数据库模板价格（缺失时兜底默认值）。
- `backend/app/secondhand_app/views.py`：回收目录接口仅从数据库模板构建，不再使用本地价目表回退。

## 验证方式

- `python backend/manage.py check`
- 访问回收目录接口与问卷接口，确认能正常返回机型与问卷数据（前提：数据库已导入机型模板）。

