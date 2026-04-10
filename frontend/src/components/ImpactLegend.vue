<template>
  <div class="legend">
    <span class="legend-item">
      <span class="dot low"></span> {{ $t('carbon.legend.lowest') }}
    </span>
    <span class="legend-item">
      <span class="dot medium"></span> {{ $t('carbon.legend.medium') }}
    </span>
    <span class="legend-item">
      <span class="dot high"></span> {{ $t('carbon.legend.highest') }}
    </span>
  </div>
</template>

<style scoped>
.legend {
  color: #888;
  display: flex;
  font-size: 0.75rem;
  gap: 1.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
}

.legend-item {
  align-items: center;
  display: flex;
  gap: 0.5rem;
}

.dot {
  border-radius: 50%;
  height: 8px;
  width: 8px;
}

.dot.low {
  background: #00aa3c;
}
.dot.medium {
  background: #fb923c;
}
.dot.high {
  background: #ff5252;
}
</style>
