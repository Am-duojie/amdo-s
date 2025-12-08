<template>
  <div class="tags-view" @contextmenu.prevent>
    <div
      v-for="tag in visitedViews"
      :key="tag.fullPath"
      class="tag-item"
      :class="{ active: tag.fullPath === route.fullPath }"
      @click="toView(tag)"
      @contextmenu.prevent="openMenu($event, tag)"
    >
      <span class="tag-title">{{ tag.title }}</span>
      <el-icon v-if="!tag.affix" class="tag-close" @click.stop="closeView(tag)">
        <Close />
      </el-icon>
    </div>
    <ul v-show="menu.visible" class="context-menu" :style="{ left: menu.x + 'px', top: menu.y + 'px' }">
      <li @click="refreshView(menu.tag)">刷新</li>
      <li @click="closeView(menu.tag)" :class="{ disabled: menu.tag?.affix }">关闭</li>
      <li @click="closeOthers(menu.tag)">关闭其他</li>
      <li @click="closeAll()">关闭全部</li>
    </ul>
  </div>
</template>

<script setup>
import { reactive, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Close } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const visitedViews = reactive([])

const addView = (r) => {
  if (!r.meta?.title) return
  if (visitedViews.some(v => v.fullPath === r.fullPath)) return
  visitedViews.push({
    title: r.meta.title,
    fullPath: r.fullPath,
    affix: r.meta.affix === true
  })
}

const closeView = (view) => {
  const index = visitedViews.findIndex(v => v.fullPath === view.fullPath)
  if (index === -1) return
  const isActive = route.fullPath === view.fullPath
  visitedViews.splice(index, 1)
  if (isActive && visitedViews.length) {
    const target = visitedViews[Math.max(index - 1, 0)]
    router.push(target.fullPath)
  }
}

const toView = (view) => {
  if (view.fullPath !== route.fullPath) router.push(view.fullPath)
}

const closeOthers = (view) => {
  if (!view) return
  const fixed = visitedViews.filter(v => v.affix)
  const target = visitedViews.find(v => v.fullPath === view.fullPath)
  visitedViews.splice(0, visitedViews.length, ...(target ? [...fixed, target] : fixed))
  if (target) toView(target)
}

const closeAll = () => {
  const fixed = visitedViews.filter(v => v.affix)
  visitedViews.splice(0, visitedViews.length, ...fixed)
  if (fixed.length) toView(fixed[0])
}

const refreshView = (view) => {
  if (!view) return
  router.replace({ path: '/redirect' + view.fullPath })
}

const menu = reactive({ visible: false, x: 0, y: 0, tag: null })

const openMenu = (e, tag) => {
  menu.visible = true
  menu.x = e.clientX
  menu.y = e.clientY
  menu.tag = tag
}

const hideMenu = () => {
  menu.visible = false
  menu.tag = null
}

onMounted(() => {
  document.addEventListener('click', hideMenu)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', hideMenu)
})

watch(
  () => route.fullPath,
  () => addView(route),
  { immediate: true }
)
</script>

<style scoped>
.tags-view {
  display: flex;
  flex-wrap: nowrap;
  gap: 6px;
  padding: 6px 0;
  overflow-x: auto;
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding-left: 8px;
}

.tags-view::-webkit-scrollbar {
  height: 6px;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 10px;
  height: 26px;
  background: #f0f2f5;
  border: 1px solid #d8d8d8;
  border-radius: 2px;
  font-size: 13px;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-item:hover {
  background: #fff;
  border-color: #c0c4cc;
}

.tag-item.active {
  background: #fff;
  border-color: #409eff;
  color: #409eff;
  font-weight: 600;
}

.tag-close {
  font-size: 14px;
}

.context-menu {
  position: fixed;
  z-index: 2000;
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 4px 0;
  list-style: none;
  box-shadow: 0 2px 12px rgba(0,0,0,0.12);
  min-width: 120px;
}

.context-menu li {
  padding: 6px 12px;
  font-size: 13px;
  color: #303133;
  cursor: pointer;
}

.context-menu li:hover {
  background: #ecf5ff;
  color: #409eff;
}

.context-menu li.disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}
</style>

