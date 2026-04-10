<template>
  <div class="unit-toggle">
    <button
      :class="{ active: modelValue === 'kg' }"
      @click="$emit('update:modelValue', 'kg')"
    >
      kgCO2e
    </button>
    <button
      :class="{ active: modelValue === 't' }"
      @click="$emit('update:modelValue', 't')"
    >
      tCO2e
    </button>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true
  }
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.unit-toggle {
  background: var(--bg-card);
  border: 3px solid var(--bg-card);
  border-radius: 6px;
  display: flex;
  overflow: hidden;
}

.unit-toggle button {
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.75rem;
  padding: 0.5rem 0.75rem;
}

.unit-toggle button.active {
  background: var(--bg-surface);
  color: var(--text-heading);
}
</style>
