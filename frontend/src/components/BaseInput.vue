<template>
  <div class="base-input-wrapper" :class="wrapperClass">
    <label v-if="label" :for="inputId" class="input-label">
      {{ label }}
      <span v-if="required" class="required-mark">*</span>
    </label>
    
    <div class="input-container">
      <span v-if="prefixIcon || $slots.prefix" class="input-prefix">
        <slot name="prefix">{{ prefixIcon }}</slot>
      </span>
      
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :maxlength="maxlength"
        class="input-field"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
      />
      
      <span v-if="suffixIcon || $slots.suffix || showClear" class="input-suffix">
        <button 
          v-if="showClear && modelValue" 
          type="button"
          class="clear-btn"
          @click="handleClear"
        >
          ✕
        </button>
        <slot name="suffix">{{ suffixIcon }}</slot>
      </span>
    </div>
    
    <div v-if="error || hint" class="input-message">
      <span v-if="error" class="error-message">{{ error }}</span>
      <span v-else-if="hint" class="hint-message">{{ hint }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  label: String,
  type: {
    type: String,
    default: 'text'
  },
  placeholder: String,
  disabled: Boolean,
  readonly: Boolean,
  required: Boolean,
  error: String,
  hint: String,
  prefixIcon: String,
  suffixIcon: String,
  clearable: Boolean,
  maxlength: [String, Number],
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  }
})

const emit = defineEmits(['update:modelValue', 'focus', 'blur', 'clear'])

const inputId = `input-${Math.random().toString(36).substr(2, 9)}`
const isFocused = ref(false)

const wrapperClass = computed(() => [
  `input-size-${props.size}`,
  {
    'is-disabled': props.disabled,
    'is-focused': isFocused.value,
    'has-error': props.error
  }
])

const showClear = computed(() => props.clearable && !props.disabled && !props.readonly)

const handleInput = (e) => {
  emit('update:modelValue', e.target.value)
}

const handleFocus = (e) => {
  isFocused.value = true
  emit('focus', e)
}

const handleBlur = (e) => {
  isFocused.value = false
  emit('blur', e)
}

const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
}
</script>

<style scoped>
.base-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  font-size: 13px;
  font-weight: 500;
  color: #111827;
}

.required-mark {
  color: #ef4444;
  margin-left: 2px;
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #e6e8ee;
  border-radius: 12px;
  transition: all 0.2s;
}

.input-container:hover:not(.is-disabled) {
  border-color: #d1d5db;
}

.is-focused .input-container {
  border-color: #ff6a00;
  box-shadow: 0 0 0 3px rgba(255, 106, 0, 0.1);
}

.has-error .input-container {
  border-color: #ef4444;
}

.input-field {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: #111827;
  width: 100%;
}

.input-field::placeholder {
  color: #9ca3af;
}

.input-size-sm .input-field {
  height: 32px;
  padding: 0 12px;
  font-size: 13px;
}

.input-size-md .input-field {
  height: 40px;
  padding: 0 16px;
  font-size: 14px;
}

.input-size-lg .input-field {
  height: 48px;
  padding: 0 20px;
  font-size: 16px;
}

.input-prefix,
.input-suffix {
  display: flex;
  align-items: center;
  color: #9ca3af;
}

.input-prefix {
  padding-left: 16px;
}

.input-suffix {
  padding-right: 16px;
}

.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: #f3f4f6;
  border-radius: 50%;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.15s;
  font-size: 12px;
}

.clear-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

.input-message {
  font-size: 12px;
}

.error-message {
  color: #ef4444;
}

.hint-message {
  color: #6b7280;
}

.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
