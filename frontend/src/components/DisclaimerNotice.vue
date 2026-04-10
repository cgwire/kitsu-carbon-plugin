<template>
  <div class="disclaimer" role="note">
    <triangle-alert :size="16" class="disclaimer-icon" />
    <p>{{ $t('carbon.disclaimer') }}</p>
  </div>
</template>

<script setup>
import { TriangleAlert } from 'lucide-vue-next'
</script>

<style scoped>
.disclaimer {
  align-items: flex-start;
  background: #2f3136;
  border: 1px solid #42464e;
  border-left: 3px solid #fb923c;
  border-radius: 6px;
  color: #aaa;
  display: flex;
  font-size: 0.75rem;
  gap: 0.625rem;
  line-height: 1.5;
  margin-top: 1rem;
  padding: 0.625rem 0.875rem;
}

.disclaimer-icon {
  color: #fb923c;
  flex-shrink: 0;
  margin-top: 1px;
}

.disclaimer p {
  margin: 0;
}
</style>
