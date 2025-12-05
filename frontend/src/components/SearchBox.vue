<template>
  <div class="search-section">
    <div class="search-box">
      <input
        class="search-input"
        :placeholder="placeholder"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        @keyup.enter="$emit('search')"
      />
      <button class="search-btn" @click="$emit('search')">
        <span class="search-icon">🔍</span>{{ buttonText }}
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '搜索二手好物' },
  buttonText: { type: String, default: '搜索' }
})
defineEmits(['update:modelValue', 'search'])
</script>

<style scoped>
.search-section { 
  flex: 1;
  max-width: 620px;
}

.search-box {
  display: flex;
  height: 44px;
  background: var(--bg-white);
  border-radius: 22px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.search-box .search-input {
  flex: 1;
  border: none;
  padding: 0 20px;
  font-size: 14px;
  outline: none;
  background: transparent;
}
.search-box .search-input::placeholder { color: var(--text-light); }

.search-box .search-btn {
  padding: 0 24px;
  background: var(--brand-orange);
  border: none;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: background 0.2s;
}
.search-box .search-btn:hover { background: #ff7722; }
.search-box .search-btn .search-icon { font-size: 13px; }
</style>
