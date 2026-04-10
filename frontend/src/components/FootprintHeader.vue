<template>
  <header class="header">
    <div class="header-left">
      <h1>{{ $t('carbon.title') }}</h1>
      <span class="subtitle">{{ subtitle }}</span>
    </div>
    <div class="header-right">
      <unit-toggle
        :model-value="unit"
        @update:model-value="$emit('update:unit', $event)"
      />
      <button class="info-btn" @click="$emit('show-info')">
        <info :size="20" />
      </button>
    </div>
  </header>
</template>

<script setup>
import { Info } from 'lucide-vue-next'
import UnitToggle from './UnitToggle.vue'

defineProps({
  subtitle: {
    type: String,
    required: true
  },
  unit: {
    type: String,
    required: true
  }
})
defineEmits(['update:unit', 'show-info'])
</script>

<style scoped>
.header {
  align-items: flex-start;
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.header-left h1 {
  color: var(--text-heading);
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.header-right {
  align-items: center;
  display: flex;
  gap: 0.75rem;
}

.info-btn {
  align-items: center;
  background: transparent;
  border: 1px solid var(--border-secondary);
  border-radius: 50%;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  height: 32px;
  justify-content: center;
  width: 32px;
}

.info-btn:hover {
  border-color: var(--border-light);
  color: var(--text-heading);
}

@media (max-width: 768px) {
  .header {
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .header-left {
    width: 100%;
  }

  .header-right {
    justify-content: space-between;
    width: 100%;
  }
}
</style>
