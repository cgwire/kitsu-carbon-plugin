<template>
  <div class="carbon-tracking">
    <header class="header">
      <div class="header-left">
        <h1>Carbon Tracking</h1>
        <span class="subtitle">{{ projectName }}</span>
      </div>
      <div class="header-right">
        <div class="unit-toggle">
          <button :class="{ active: unit === 'kg' }" @click="unit = 'kg'">
            kgCO2e
          </button>
          <button :class="{ active: unit === 't' }" @click="unit = 't'">
            tCO2e
          </button>
        </div>
        <button class="info-btn" @click="showInfo = true">
          <info :size="20" />
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
            <cloud :size="20" />
          </div>
          <div class="stat-value">
            <span class="value">{{ formatValue(data.total_co2_kg) }}</span>
            <span class="unit">{{ unit === "kg" ? "kgCO2e" : "tCO2e" }}</span>
          </div>
          <div
            v-if="data.weekly_change_percent !== undefined"
            class="weekly-change"
            :class="weeklyChangeClass"
          >
            <trending-up v-if="data.weekly_change_percent > 0" :size="14" />
            <trending-down
              v-else-if="data.weekly_change_percent < 0"
              :size="14"
            />
            <minus v-else :size="14" />
            <span>{{ weeklyChangeLabel }} vs last week</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <span>Weekly Average Emissions</span>
            <calendar :size="20" />
          </div>
          <div class="stat-value">
            <span class="value">{{ formatValue(weeklyAverage) }}</span>
            <span class="unit"
              >{{ unit === "kg" ? "kgCO2e" : "tCO2e" }} / week</span
            >
          </div>
          <div class="stat-subtitle">Based on logged time</div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <span>Total Man-Days</span>
            <users :size="20" />
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
        >
          Matrix view
        </button>
        <button
          :class="{ active: activeTab === 'breakdown' }"
          @click="activeTab = 'breakdown'"
        >
          Step breakdown
        </button>
      </div>

      <div v-if="activeTab === 'matrix'" class="matrix-view table-scroll">
        <table class="matrix-table">
          <thead>
            <tr>
              <th>TASK TYPES</th>
              <th style="text-align: center">ALL</th>
              <th
                v-for="tt in taskTypes"
                :key="tt"
                :style="taskTypeHeaderStyle(tt)"
              >
                {{ tt }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr class="total-row">
              <td>All Task Types</td>
              <td>
                {{ formatValue(data.total_co2_kg) }}
              </td>
              <td
                v-for="tt in taskTypes"
                :key="tt"
                :style="taskTypeCellStyle(tt)"
              >
                {{ formatValue(getTaskTypeTotal(tt)) }}
              </td>
            </tr>
            <tr v-for="item in sortedByEmission" :key="item.task_type_id">
              <td>{{ item.task_type_name }}</td>
              <td>
                {{ formatValue(item.co2_kg) }}
              </td>
              <td
                v-for="tt in taskTypes"
                :key="tt"
                :class="
                  getImpactClass(item.task_type_name === tt ? item.co2_kg : 0)
                "
                :style="taskTypeCellStyle(tt)"
              >
                {{
                  item.task_type_name === tt ? formatValue(item.co2_kg) : "-"
                }}
              </td>
            </tr>
          </tbody>
        </table>
        <div class="legend">
          <span class="legend-item">
            <span class="dot low"></span> Lowest Impact
          </span>
          <span class="legend-item">
            <span class="dot medium"></span> Medium Impact
          </span>
          <span class="legend-item">
            <span class="dot high"></span> Highest Impact
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
            <tr
              v-for="item in sortedByEmission"
              :key="item.task_type_id"
              :style="taskTypeRowStyle(item.task_type_name)"
            >
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
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="info-modal-title">
        <div class="modal-header">
          <h2 id="info-modal-title">How is carbon calculated?</h2>
          <button class="close-btn" @click="showInfo = false">&times;</button>
        </div>
        <p class="modal-text">
          Emissions are estimated based on logged working time per task and
          geographic carbon factors specific to each production facility.
        </p>
        <div class="formula">
          <span>Work Time</span>
          <span class="operator">x</span>
          <span>People</span>
          <span class="operator">x</span>
          <span class="highlight">Carbon Factor</span>
        </div>
        <div class="factors-section">
          <h3>WHAT'S INCLUDED IN THE CARBON FACTOR :</h3>
          <div class="factor-grid">
            <div class="factor-item">
              <monitor :size="18" />
              <span>Workstation</span>
            </div>
            <div class="factor-item">
              <building2 :size="18" />
              <span>Building Energy</span>
            </div>
            <div class="factor-item">
              <zap :size="18" />
              <span>Electricity Mix</span>
            </div>
            <div class="factor-item">
              <utensils-crossed :size="18" />
              <span>Meals</span>
            </div>
            <div class="factor-item">
              <cloud :size="18" />
              <span>Cloud & Infra</span>
            </div>
            <div class="factor-item">
              <train-front :size="18" />
              <span>Commute</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import {
  Cloud,
  Calendar,
  Users,
  Info,
  Monitor,
  Building2,
  Zap,
  UtensilsCrossed,
  TrainFront,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-vue-next";
import { useMainStore } from "../stores/main";

const store = useMainStore();

const props = defineProps({
  productionId: {
    type: String,
    required: true,
  },
});

const loading = ref(true);
const error = ref(null);
const unit = ref(localStorage.getItem("carbon-unit") || "kg");
const activeTab = ref(localStorage.getItem("carbon-tab") || "matrix");

watch(unit, (v) => localStorage.setItem("carbon-unit", v));
watch(activeTab, (v) => localStorage.setItem("carbon-tab", v));
const showInfo = ref(false);
const projectName = ref("");
const data = ref({
  details: [],
  total_co2_kg: 0,
  total_man_days: 0,
});

const allTaskTypes = computed(() => {
  if (store.taskTypes.length > 0) {
    return store.taskTypes.map((tt) => tt.name).sort();
  }
  const types = new Set();
  data.value.details.forEach((item) => types.add(item.task_type_name));
  return Array.from(types).sort();
});

const taskTypes = computed(() => {
  return allTaskTypes.value.filter((tt) => {
    return data.value.details.some(
      (item) => item.task_type_name === tt && item.co2_kg > 0,
    );
  });
});

const sortedByEmission = computed(() => {
  return [...data.value.details].sort((a, b) => b.co2_kg - a.co2_kg);
});

const maxEmission = computed(() => {
  if (data.value.details.length === 0) return 1;
  return Math.max(...data.value.details.map((d) => d.co2_kg));
});

const weeklyChangeClass = computed(() => {
  const pct = data.value.weekly_change_percent || 0;
  if (pct > 0) return "change-up";
  if (pct < 0) return "change-down";
  return "change-neutral";
});

const weeklyChangeLabel = computed(() => {
  const pct = data.value.weekly_change_percent || 0;
  if (pct > 0) return `+${pct}%`;
  if (pct < 0) return `${pct}%`;
  return "0%";
});

const weeklyAverage = computed(() => {
  const prod = store.openProductions.find((p) => p.id === props.productionId);
  if (!prod || !prod.start_date) return 0;
  const start = new Date(prod.start_date);
  const end = prod.end_date ? new Date(prod.end_date) : new Date();
  const ms = end - start;
  const weeks = Math.max(ms / (7 * 24 * 60 * 60 * 1000), 1);
  return data.value.total_co2_kg / weeks;
});

function formatValue(kg) {
  if (unit.value === "t") {
    return (kg / 1000).toFixed(2);
  }
  if (kg >= 1000) {
    return Math.round(kg).toLocaleString();
  }
  if (kg >= 1) {
    return kg.toFixed(1);
  }
  return kg.toFixed(2);
}

function formatNumber(num) {
  return Math.round(num).toLocaleString();
}

function getImpactClass(kg) {
  if (kg === null || kg === undefined || kg === 0) return "";
  const max = maxEmission.value;
  if (max === 0) return "low";
  const ratio = kg / max;
  if (ratio >= 0.66) return "high";
  if (ratio >= 0.33) return "medium";
  return "low";
}

function getTaskTypeTotal(taskTypeName) {
  const item = data.value.details.find(
    (d) => d.task_type_name === taskTypeName,
  );
  return item ? item.co2_kg : 0;
}

function getTaskTypeColor(taskTypeName) {
  const tt = store.taskTypes.find(
    (t) =>
      t.name === taskTypeName ||
      t.name.toLowerCase() === taskTypeName.toLowerCase(),
  );
  return tt?.color || null;
}

function taskTypeHeaderStyle(taskTypeName) {
  const color = getTaskTypeColor(taskTypeName);
  if (!color) return {};
  return {
    borderLeft: `2px solid ${color}30`,
    background: `${color}10`,
    textAlign: "center",
  };
}

function taskTypeRowStyle(taskTypeName) {
  const color = getTaskTypeColor(taskTypeName);
  if (!color) return {};
  return {
    background: `${color}10`,
    borderBottom: `2px solid ${color}`,
  };
}

function taskTypeCellStyle(taskTypeName) {
  const color = getTaskTypeColor(taskTypeName);
  if (!color) return {};
  return {
    borderLeft: `2px solid ${color}30`,
    borderRight: `1px solid ${color}30`,
    background: `${color}08`,
  };
}

function getBarWidth(kg) {
  return (kg / maxEmission.value) * 100;
}

function getPercent(kg) {
  if (data.value.total_co2_kg === 0) return "0.0";
  return ((kg / data.value.total_co2_kg) * 100).toFixed(1);
}

async function fetchData() {
  loading.value = true;
  error.value = null;

  try {
    const response = await fetch(
      `/api/plugins/carbon/productions/${props.productionId}/footprint/task-types`,
    );
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const result = await response.json();
    data.value = result;
    projectName.value = result.project_name || "";
  } catch (err) {
    error.value = `Failed to load data: ${err.message}`;
  } finally {
    loading.value = false;
  }
}

watch(() => props.productionId, () => fetchData(), { immediate: true });

function onKeydown(e) {
  if (e.key === "Escape") showInfo.value = false;
}

onMounted(() => {
  window.addEventListener("keydown", onKeydown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", onKeydown);
});
</script>

<style scoped>
.carbon-tracking {
  background: #36393f;
  color: #e0e0e0;
  min-height: 100vh;
  padding: 1.5rem;
  font-family:
    -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
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
  background: #202225;
  border: 3px solid #202225;
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
  border-radius: 4px;
}

.unit-toggle button.active {
  background: #42464e;
  color: #fff;
}

.info-btn {
  background: transparent;
  border: 1px solid #2f3136;
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

.loading,
.error {
  text-align: center;
  padding: 2rem;
  color: #888;
}

.error {
  color: #ff5252;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: #202225;
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

.weekly-change {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.5rem;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.weekly-change.change-up {
  background: rgba(255, 82, 82, 0.15);
  color: #ff5252;
}

.weekly-change.change-down {
  background: rgba(0, 170, 60, 0.15);
  color: #00aa3c;
}

.weekly-change.change-neutral {
  background: rgba(136, 136, 136, 0.15);
  color: #888;
}

.tabs {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid #202225;
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
  content: "";
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #00aa3c;
}

.table-scroll {
  overflow-x: auto;
}

.matrix-table {
  width: 100%;
  min-width: max-content;
  border-collapse: collapse;
  font-size: 0.875rem;
  border: 1px solid #202225;
  border-radius: 6px;
  overflow: hidden;
}

.matrix-table th,
.matrix-table td {
  min-width: 120px;
}

.matrix-table th {
  text-align: left;
  padding: 0.75rem;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #202225;
  background: #42464e;
}

.matrix-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #202225;
  text-align: center;
}

.matrix-table td:first-child {
  color: #e0e0e0;
  text-align: left;
}

.matrix-table tbody tr:nth-child(odd) {
  background: #46494f;
}

.matrix-table tbody tr:nth-child(even) {
  background: #36393f;
}

.matrix-table .total-row {
  background: #4f525a !important;
}

.matrix-table .total-row td:first-child {
  font-weight: 600;
}

.matrix-table td.low {
  color: #00aa3c;
}
.matrix-table td.medium {
  color: #fb923c;
}
.matrix-table td.high {
  color: #ff5252;
}

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

.dot.low {
  background: #00aa3c;
}
.dot.medium {
  background: #fb923c;
}
.dot.high {
  background: #ff5252;
}

.breakdown-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #202225;
  border-radius: 6px;
  overflow: hidden;
}

.breakdown-table th {
  text-align: left;
  padding: 0.75rem;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #202225;
  background: #42464e;
}

.breakdown-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #202225;
}

.breakdown-table td:first-child {
  width: 150px;
  font-weight: 500;
}

.bar-cell {
  width: 60%;
}

.bar-track {
  background: #202225;
  height: 24px;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.bar-fill.low {
  background: #00aa3c;
}
.bar-fill.medium {
  background: #fb923c;
}
.bar-fill.high {
  background: #ff5252;
}

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
  background: #36393f;
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 520px;
  width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #fff;
  font-weight: 600;
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
  color: #888;
  font-size: 0.875rem;
  line-height: 1.6;
  margin-bottom: 1.25rem;
}

.formula {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1.25rem;
  background: #202225;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-family: monospace;
  font-size: 1rem;
  color: #e0e0e0;
}

.formula .operator {
  color: #666;
  font-size: 0.875rem;
}

.formula .highlight {
  color: #00aa3c;
}

.factors-section h3 {
  font-size: 0.7rem;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.factor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.factor-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #42464e;
  padding: 0.875rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #ccc;
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
