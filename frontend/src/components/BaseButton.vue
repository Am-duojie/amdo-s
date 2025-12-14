<template>
  <button 
    :class="buttonClass" 
    :disabled="disabled || loading"
    :type="nativeType"
    @click="handleClick"
  >
    <span v-if="loading" class="btn-loading">
      <span class="spinner"></span>
    </span>
    <span v-if="icon && !loading" class="btn-icon">{{ icon }}</span>
    <span v-if="$slots.default" class="btn-text">
      <slot></slot>
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'secondary', 'outline', 'ghost', 'danger', 'success'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  },
  icon: String,
  loading: Boolean,
  disabled: Boolean,
  block: Boolean,
  nativeType: {
    type: String,
    default: 'button'
  }
})

const emit = defineEmits(['click'])

const buttonClass = computed(() => [
  'base-button',
  `btn-${props.variant}`,
  `btn-${props.size}`,
  {
    'btn-loading': props.loading,
    'btn-disabled': props.disabled,
    'btn-block': props.block
  }
])

const handleClick = (e) => {
  if (!props.disabled && !props.loading) {
    emit('click', e)
  }
}
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-sm {
  height: 32px;
  padding: 0 12px;
  font-size: 13px;
}

.btn-md {
  height: 40px;
  padding: 0 20px;
  font-size: 14px;
}

.btn-lg {
  height: 48px;
  padding: 0 24px;
  font-size: 16px;
}

.btn-primary {
  background: linear-gradient(135deg, #ff6a00, #ffd700);
  color: #333;
}

.btn-primary:hover:not(.btn-disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 106, 0, 0.3);
}

.btn-secondary {
  background: #f3f4f6;
  color: #111827;
  border: 1px solid #e6e8ee;
}

.btn-secondary:hover:not(.btn-disabled) {
  background: #e5e7eb;
}

.btn-outline {
  background: transparent;
  color: #ff6a00;
  border: 2px solid #ff6a00;
}

.btn-outline:hover:not(.btn-disabled) {
  background: rgba(255, 106, 0, 0.1);
}

.btn-ghost {
  background: transparent;
  color: #111827;
}

.btn-ghost:hover:not(.btn-disabled) {
  background: #f3f4f6;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(.btn-disabled) {
  background: #dc2626;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(.btn-disabled) {
  background: #059669;
}

.btn-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-block {
  width: 100%;
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
