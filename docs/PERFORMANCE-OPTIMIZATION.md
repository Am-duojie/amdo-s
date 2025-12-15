# 性能优化建议 - 回收系统

**创建时间**: 2025-12-15

## 一、后端性能优化

### 1.1 数据库索引优化

```sql
-- 回收订单表索引
CREATE INDEX idx_recycleorder_template_status 
ON secondhand_app_recycleorder(template_id, status);

CREATE INDEX idx_recycleorder_user_created 
ON secondhand_app_recycleorder(user_id, created_at DESC);

CREATE INDEX idx_recycleorder_status_created 
ON secondhand_app_recycleorder(status, created_at DESC);

-- 官方验商品表索引
CREATE INDEX idx_verifiedproduct_template_status 
ON secondhand_app_verifiedproduct(template_id, status);

CREATE INDEX idx_verifiedproduct_category_status 
ON secondhand_app_verifiedproduct(category_id, status);

CREATE INDEX idx_verifiedproduct_created 
ON secondhand_app_verifiedproduct(created_at DESC);

-- 机型模板表索引
CREATE INDEX idx_template_device_brand_model 
ON admin_api_recycledevicetemplate(device_type, brand, model);

CREATE INDEX idx_template_active 
ON admin_api_recycledevicetemplate(is_active);

-- 问卷模板表索引
CREATE INDEX idx_question_template_active 
ON admin_api_recyclequestiontemplate(device_template_id, is_active, step_order);

-- 问卷选项表索引
CREATE INDEX idx_option_question_active 
ON admin_api_recyclequestionoption(question_template_id, is_active, option_order);
```

### 1.2 查询优化

**优化前**:
```python
# 问题: N+1 查询
orders = RecycleOrder.objects.all()
for order in orders:
    print(order.user.username)  # 每次都查询数据库
    print(order.template.brand)  # 每次都查询数据库
```

**优化后**:
```python
# 使用 select_related 预加载关联对象
orders = RecycleOrder.objects.select_related('user', 'template').all()
for order in orders:
    print(order.user.username)  # 不再查询数据库
    print(order.template.brand)  # 不再查询数据库
```

**应用到视图**:
```python
# backend/app/secondhand_app/views.py

class RecycleOrderViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return RecycleOrder.objects.select_related(
            'user',
            'template',
            'template__category'
        ).prefetch_related(
            'template__questions',
            'template__questions__options'
        ).filter(user=self.request.user)
```

### 1.3 缓存优化

```python
# backend/app/secondhand_app/views.py
from django.core.cache import cache
from django.views.decorators.cache import cache_page

class RecycleCatalogView(APIView):
    def get(self, request):
        device_type = request.query_params.get('device_type')
        brand = request.query_params.get('brand')
        
        # 生成缓存键
        cache_key = f"recycle_catalog:{device_type}:{brand}"
        
        # 尝试从缓存获取
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # 查询数据库
        data = self._build_catalog_from_templates(device_type, brand, None, '')
        
        # 缓存 15 分钟
        cache.set(cache_key, data, 900)
        
        return Response(data)
```

### 1.4 分页优化

```python
# 使用游标分页代替偏移分页（大数据量时更快）
from rest_framework.pagination import CursorPagination

class RecycleOrderCursorPagination(CursorPagination):
    page_size = 20
    ordering = '-created_at'

class RecycleOrderViewSet(viewsets.ModelViewSet):
    pagination_class = RecycleOrderCursorPagination
```

---

## 二、前端性能优化

### 2.1 问卷数据缓存

```typescript
// frontend/src/stores/questionnaireCache.ts
import { defineStore } from 'pinia';

export const useQuestionnaireCache = defineStore('questionnaireCache', {
  state: () => ({
    cache: new Map<string, any>(),
  }),
  
  actions: {
    get(deviceType: string, brand: string, model: string) {
      const key = `${deviceType}-${brand}-${model}`;
      return this.cache.get(key);
    },
    
    set(deviceType: string, brand: string, model: string, data: any) {
      const key = `${deviceType}-${brand}-${model}`;
      this.cache.set(key, data);
      
      // 限制缓存大小（最多 50 个）
      if (this.cache.size > 50) {
        const firstKey = this.cache.keys().next().value;
        this.cache.delete(firstKey);
      }
    },
    
    clear() {
      this.cache.clear();
    },
  },
});
```

**使用缓存**:
```typescript
// frontend/src/pages/RecycleEstimateWizard.vue
import { useQuestionnaireCache } from '@/stores/questionnaireCache';

const cache = useQuestionnaireCache();

async function loadQuestionTemplate() {
  // 先检查缓存
  const cached = cache.get(deviceType.value, brand.value, model.value);
  if (cached) {
    templateFromBackend.value = cached;
    return;
  }
  
  // 从 API 加载
  const { data } = await getRecycleQuestionTemplate({
    device_type: deviceType.value,
    brand: brand.value,
    model: model.value,
  });
  
  // 保存到缓存
  cache.set(deviceType.value, brand.value, model.value, data);
  templateFromBackend.value = data;
}
```

### 2.2 图片懒加载

```vue
<!-- 使用原生 loading="lazy" -->
<template>
  <img 
    :src="template.default_cover_image" 
    loading="lazy"
    alt="机型图片"
    @error="handleImageError"
  />
</template>

<script setup>
function handleImageError(e) {
  // 图片加载失败时显示占位图
  e.target.src = '/placeholder.png';
}
</script>
```

### 2.3 列表虚拟滚动

```vue
<!-- 当机型列表很长时使用虚拟滚动 -->
<template>
  <RecycleScroller
    :items="modelList"
    :item-size="80"
    key-field="id"
    v-slot="{ item }"
  >
    <div class="model-item">
      {{ item.name }}
    </div>
  </RecycleScroller>
</template>

<script setup>
import { RecycleScroller } from 'vue-virtual-scroller';
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';
</script>
```

### 2.4 防抖和节流

```typescript
// frontend/src/pages/RecycleEstimateWizard.vue
import { debounce } from 'lodash-es';

// 估价 API 调用使用防抖（300ms）
const debouncedEstimate = debounce(async () => {
  await runEstimate();
}, 300);

watch(
  () => [selectedStorage.value, draft.condition],
  () => {
    debouncedEstimate();
  }
);
```

### 2.5 代码分割

```typescript
// frontend/src/router/index.ts
const routes = [
  {
    path: '/recycle/estimate',
    name: 'RecycleEstimate',
    // 懒加载，减少首屏加载时间
    component: () => import('@/pages/RecycleEstimateWizard.vue'),
  },
  {
    path: '/admin/recycle-templates',
    name: 'RecycleTemplates',
    component: () => import('@/admin/pages/RecycleTemplates.vue'),
  },
];
```

---

## 三、网络优化

### 3.1 API 请求合并

**优化前**:
```typescript
// 3 个独立请求
const catalog = await getRecycleCatalog();
const template = await getRecycleTemplate(id);
const questionnaire = await getRecycleQuestionTemplate(id);
```

**优化后**:
```typescript
// 1 个请求返回所有数据
const { catalog, template, questionnaire } = await getRecycleData(id);
```

**后端实现**:
```python
# backend/app/secondhand_app/views.py
class RecycleDataView(APIView):
    def get(self, request):
        template_id = request.query_params.get('template_id')
        
        # 一次性获取所有数据
        template = RecycleDeviceTemplate.objects.get(id=template_id)
        questions = RecycleQuestionTemplate.objects.filter(
            device_template=template
        ).prefetch_related('options')
        
        return Response({
            'template': RecycleDeviceTemplateSerializer(template).data,
            'questionnaire': RecycleQuestionTemplateSerializer(questions, many=True).data,
        })
```

### 3.2 HTTP/2 服务器推送

```nginx
# nginx 配置
location /api/recycle-templates/ {
    http2_push /api/recycle-templates/question-template/;
    proxy_pass http://backend;
}
```

### 3.3 Gzip 压缩

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',  # 添加 Gzip 中间件
    # ... 其他中间件
]
```

---

## 四、数据库优化

### 4.1 连接池配置

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 600,  # 连接池：保持连接 10 分钟
    }
}
```

### 4.2 只查询需要的字段

```python
# 优化前：查询所有字段
orders = RecycleOrder.objects.all()

# 优化后：只查询需要的字段
orders = RecycleOrder.objects.values(
    'id', 'device_type', 'brand', 'model', 'status', 'created_at'
)
```

### 4.3 批量操作

```python
# 优化前：逐个创建
for data in order_list:
    RecycleOrder.objects.create(**data)

# 优化后：批量创建
RecycleOrder.objects.bulk_create([
    RecycleOrder(**data) for data in order_list
])
```

---

## 五、监控和分析

### 5.1 性能监控

```python
# backend/middleware/performance.py
import time
import logging

logger = logging.getLogger(__name__)

class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # 记录慢请求（超过 1 秒）
        if duration > 1.0:
            logger.warning(
                f'Slow request: {request.method} {request.path} '
                f'took {duration:.2f}s'
            )
        
        # 添加响应头
        response['X-Response-Time'] = f'{duration:.3f}s'
        
        return response
```

### 5.2 前端性能监控

```typescript
// frontend/src/utils/performance.ts
export function measurePerformance(name: string, fn: () => Promise<any>) {
  return async (...args: any[]) => {
    const start = performance.now();
    
    try {
      const result = await fn(...args);
      const duration = performance.now() - start;
      
      // 记录到控制台
      console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
      
      // 发送到监控服务（可选）
      if (duration > 1000) {
        sendToMonitoring({ name, duration });
      }
      
      return result;
    } catch (error) {
      const duration = performance.now() - start;
      console.error(`[Performance] ${name} failed after ${duration.toFixed(2)}ms`);
      throw error;
    }
  };
}

// 使用
const loadQuestionTemplate = measurePerformance(
  'loadQuestionTemplate',
  async () => {
    const { data } = await getRecycleQuestionTemplate(...);
    return data;
  }
);
```

---

## 六、优化效果预期

| 优化项 | 优化前 | 优化后 | 提升 |
|-------|--------|--------|------|
| 机型目录 API | 800ms | 300ms | 62% |
| 问卷模板 API | 600ms | 250ms | 58% |
| 订单列表查询 | 1200ms | 400ms | 67% |
| 首屏加载 (FCP) | 2.5s | 1.2s | 52% |
| 页面交互 (TTI) | 4.5s | 2.5s | 44% |

---

## 七、优化优先级

### P0 - 立即优化
- ✅ 数据库索引
- ✅ N+1 查询优化
- ✅ API 缓存

### P1 - 尽快优化
- ✅ 图片懒加载
- ✅ 代码分割
- ✅ 防抖节流

### P2 - 可选优化
- ⏳ 虚拟滚动
- ⏳ HTTP/2 推送
- ⏳ 性能监控

---

## 八、实施步骤

1. **第 1 天**: 数据库索引优化
2. **第 2 天**: 查询优化和缓存
3. **第 3 天**: 前端性能优化
4. **第 4 天**: 测试和验证
5. **第 5 天**: 监控和调优

---

## 下一步

完成性能优化后，继续进行功能测试和用户体验优化。
