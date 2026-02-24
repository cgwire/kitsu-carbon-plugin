<template>
  <div class="carbon-tracking">
    <header class="header">
      <div class="header-left">
        <h1>Carbon Tracking</h1>
        <span class="subtitle">{{ projectName }}</span>
      </div>
      <div class="header-right">
        <div class="unit-toggle">
          <button
            :class="{ active: unit === 'kg' }"
            @click="unit = 'kg'"
          >kgCO2e</button>
          <button
            :class="{ active: unit === 't' }"
            @click="unit = 't'"
          >tCO2e</button>
        </div>
        <button class="info-btn" @click="showInfo = true">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 16v-4M12 8h.01"/>
          </svg>
        </button>
      </div>
    </header>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-header">
            <span>Total Project Emissions</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
            </svg>
          </div>
          <div class="stat-value">
            <span class="value">{{ formatValue(data.total_co2_kg) }}</span>
            <span class="unit">{{ unit === 'kg' ? 'kgCO2e' : 'tCO2e' }}</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <span>Weekly Average Emissions</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <div class="stat-value">
            <span class="value">{{ formatValue(weeklyAverage) }}</span>
            <span class="unit">{{ unit === 'kg' ? 'kgCO2e' : 'tCO2e' }} / week</span>
          </div>
          <div class="stat-subtitle">Based on logged time</div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <span>Total Man-Days</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <div class="stat-value">
            <span class="value">{{ formatNumber(data.total_man_days) }}</span>
            <span class="unit">logged</span>
          </div>
          <div class="stat-subtitle">Cumulative across all steps</div>
        </div>
      </div>

      <div class="tabs">
        <button
          :class="{ active: activeTab === 'matrix' }"
          @click="activeTab = 'matrix'"
        >Matrix view</button>
        <button
          :class="{ active: activeTab === 'breakdown' }"
          @click="activeTab = 'breakdown'"
        >Step breakdown</button>
      </div>

      <div v-if="activeTab === 'matrix'" class="matrix-view">
        <table class="matrix-table">
          <thead>
            <tr>
              <th>TASK TYPES</th>
              <th>ALL</th>
              <th v-for="tt in taskTypes" :key="tt">{{ tt }}</th>
            </tr>
          </thead>
          <tbody>
            <tr class="total-row">
              <td>All Task Types</td>
              <td :class="getImpactClass(data.total_co2_kg)">
                {{ formatValue(data.total_co2_kg) }}
              </td>
              <td
                v-for="tt in taskTypes"
                :key="tt"
                :class="getImpactClass(getTaskTypeTotal(tt))"
              >
                {{ formatValue(getTaskTypeTotal(tt)) }}
              </td>
            </tr>
            <tr v-for="item in sortedDetails" :key="item.task_type_id">
              <td>{{ item.task_type_name }}</td>
              <td :class="getImpactClass(item.co2_kg)">
                {{ formatValue(item.co2_kg) }}
              </td>
              <td
                v-for="tt in taskTypes"
                :key="tt"
                :class="getImpactClass(item.task_type_name === tt ? item.co2_kg : 0)"
              >
                {{ item.task_type_name === tt ? formatValue(item.co2_kg) : '-' }}
              </td>
            </tr>
          </tbody>
        </table>
        <div class="legend">
          <span class="legend-item">
            <span class="dot low"></span> Low Impact
          </span>
          <span class="legend-item">
            <span class="dot medium"></span> Medium Impact
          </span>
          <span class="legend-item">
            <span class="dot high"></span> High Impact
          </span>
        </div>
      </div>

      <div v-else class="breakdown-view">
        <table class="breakdown-table">
          <thead>
            <tr>
              <th>PRODUCTION STEP</th>
              <th>EMISSION IMPACT</th>
              <th>VALUE</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in sortedByEmission" :key="item.task_type_id">
              <td>{{ item.task_type_name }}</td>
              <td class="bar-cell">
                <div class="bar-track">
                  <div
                    class="bar-fill"
                    :class="getImpactClass(item.co2_kg)"
                    :style="{ width: getBarWidth(item.co2_kg) + '%' }"
                  ></div>
                </div>
              </td>
              <td class="value-cell">
                <span class="kg">{{ formatValue(item.co2_kg) }} kg</span>
                <span class="percent">{{ getPercent(item.co2_kg) }}%</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <div v-if="showInfo" class="modal-overlay" @click.self="showInfo = false">
      <div class="modal">
        <div class="modal-header">
          <h2>How is carbon calculated?</h2>
          <button class="close-btn" @click="showInfo = false">&times;</button>
        </div>
        <p class="modal-text">
          Emissions are estimated based on logged working time per task and
          geographic carbon factors specific to each production facility.
        </p>
        <div class="formula">
          <span>Work Time</span>
          <span class="operator">&times;</span>
          <span>People</span>
          <span class="operator">&times;</span>
          <span class="highlight">Carbon Factor</span>
        </div>
        <div class="factors-section">
          <h3>WHAT'S INCLUDED IN THE CARBON FACTOR :</h3>
          <div class="factor-tags">
            <span class="factor-tag">Workstation</span>
            <span class="factor-tag">Building Energy</span>
            <span class="factor-tag">Electricity Mix</span>
            <span class="factor-tag">Meals</span>
            <span class="factor-tag">Cloud & Infra</span>
            <span class="factor-tag">Commute</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useMainStore } from '../stores/main'

const store = useMainStore()

const props = defineProps({
  productionId: {
    type: String,
    required: true,
  },
  episodeId: {
    type: String,
    default: null,
  },
})

const loading = ref(true)
const error = ref(null)
const unit = ref('kg')
const activeTab = ref('matrix')
const showInfo = ref(false)
const projectName = ref('')
const data = ref({
  details: [],
  total_co2_kg: 0,
  total_man_days: 0,
})

const taskTypes = computed(() => {
  if (store.taskTypes.length > 0) {
    return store.taskTypes.map((tt) => tt.name).sort()
  }
  const types = new Set()
  data.value.details.forEach((item) => types.add(item.task_type_name))
  return Array.from(types).sort()
})

const sortedDetails = computed(() => {
  return [...data.value.details].sort((a, b) => b.co2_kg - a.co2_kg)
})

const sortedByEmission = computed(() => {
  return [...data.value.details].sort((a, b) => b.co2_kg - a.co2_kg)
})

const maxEmission = computed(() => {
  return Math.max(...data.value.details.map(d => d.co2_kg), 1)
})

const weeklyAverage = computed(() => {
  const totalMinutes = data.value.total_duration_minutes || 0
  const weeks = Math.max(totalMinutes / 60 / 40, 1)
  return data.value.total_co2_kg / weeks
})

function formatValue(kg) {
  if (unit.value === 't') {
    return (kg / 1000).toFixed(2)
  }
  if (kg >= 1000) {
    return Math.round(kg).toLocaleString()
  }
  if (kg >= 1) {
    return kg.toFixed(1)
  }
  return kg.toFixed(2)
}

function formatNumber(num) {
  return Math.round(num).toLocaleString()
}

function getImpactClass(kg) {
  if (kg === 0) return 'low'
  const max = maxEmission.value
  const ratio = kg / max
  if (ratio >= 0.66) return 'high'
  if (ratio >= 0.33) return 'medium'
  return 'low'
}

function getTaskTypeTotal(taskTypeName) {
  const item = data.value.details.find(d => d.task_type_name === taskTypeName)
  return item ? item.co2_kg : 0
}

function getBarWidth(kg) {
  return (kg / maxEmission.value) * 100
}

function getPercent(kg) {
  if (data.value.total_co2_kg === 0) return '0.0'
  return ((kg / data.value.total_co2_kg) * 100).toFixed(1)
}

async function fetchData() {
  loading.value = true
  error.value = null

  try {
    const response = await fetch(
      `/api/plugins/carbon/productions/${props.productionId}/footprint/task-types`
    )
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    const result = await response.json()
    data.value = result
    projectName.value = result.project_name || ''
  } catch (err) {
    error.value = `Failed to load data: ${err.message}`
  } finally {
    loading.value = false
  }
}

watch(
  [() => props.productionId, () => props.episodeId],
  () => {
    fetchData()
  },
  { immediate: true }
)
</script>

<style scoped>
.carbon-tracking {
  background: #1e1e2e;
  color: #e0e0e0;
  min-height: 100vh;
  padding: 1.5rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.header-left h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #fff;
}

.subtitle {
  color: #888;
  font-size: 0.875rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.unit-toggle {
  display: flex;
  background: #2a2a3e;
  border-radius: 6px;
  overflow: hidden;
}

.unit-toggle button {
  background: transparent;
  border: none;
  color: #888;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  font-size: 0.75rem;
}

.unit-toggle button.active {
  background: #3a3a4e;
  color: #fff;
}

.info-btn {
  background: transparent;
  border: 1px solid #3a3a4e;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #888;
}

.info-btn:hover {
  color: #fff;
  border-color: #4a4a5e;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  color: #888;
}

.error {
  color: #f87171;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: #2a2a3e;
  border-radius: 8px;
  padding: 1rem 1.25rem;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #888;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.stat-header svg {
  opacity: 0.5;
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.stat-value .value {
  font-size: 2rem;
  font-weight: 600;
  color: #fff;
}

.stat-value .unit {
  color: #888;
  font-size: 0.875rem;
}

.stat-subtitle {
  color: #666;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.tabs {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid #2a2a3e;
}

.tabs button {
  background: transparent;
  border: none;
  color: #888;
  padding: 0.75rem 0;
  cursor: pointer;
  font-size: 0.875rem;
  position: relative;
}

.tabs button.active {
  color: #fff;
}

.tabs button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #06b6d4;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.matrix-table th {
  text-align: left;
  padding: 0.75rem;
  color: #666;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #2a2a3e;
}

.matrix-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #2a2a3e;
}

.matrix-table td:first-child {
  color: #e0e0e0;
}

.matrix-table .total-row {
  background: #252535;
}

.matrix-table .total-row td:first-child {
  font-weight: 600;
}

.matrix-table td.low { color: #22c55e; }
.matrix-table td.medium { color: #f97316; }
.matrix-table td.high { color: #f87171; }

.legend {
  display: flex;
  gap: 1.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  font-size: 0.75rem;
  color: #888;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.low { background: #22c55e; }
.dot.medium { background: #f97316; }
.dot.high { background: #f87171; }

.breakdown-table {
  width: 100%;
  border-collapse: collapse;
}

.breakdown-table th {
  text-align: left;
  padding: 0.75rem;
  color: #666;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #2a2a3e;
}

.breakdown-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #2a2a3e;
}

.breakdown-table td:first-child {
  width: 150px;
  font-weight: 500;
}

.bar-cell {
  width: 60%;
}

.bar-track {
  background: #2a2a3e;
  height: 24px;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.bar-fill.low { background: #22c55e; }
.bar-fill.medium { background: #f97316; }
.bar-fill.high { background: #f87171; }

.value-cell {
  text-align: right;
  white-space: nowrap;
}

.value-cell .kg {
  display: block;
  font-weight: 600;
}

.value-cell .percent {
  display: block;
  color: #666;
  font-size: 0.75rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: #2a2a3e;
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 480px;
  width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.125rem;
  color: #fff;
}

.close-btn {
  background: transparent;
  border: none;
  color: #888;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.close-btn:hover {
  color: #fff;
}

.modal-text {
  color: #aaa;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 1.25rem;
}

.formula {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #1e1e2e;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 0.875rem;
}

.formula .operator {
  color: #666;
}

.formula .highlight {
  color: #22c55e;
  font-weight: 600;
}

.factors-section h3 {
  font-size: 0.7rem;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.factor-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.factor-tag {
  background: #3a3a4e;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #ccc;
}
</style>
