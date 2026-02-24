import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMainStore = defineStore('main', () => {
  const taskTypes = ref([])
  const openProductions = ref([])
  const sequences = ref([])
  const episodes = ref([])
  const assetTypes = ref([])

  async function fetchTaskTypes() {
    const response = await fetch('/api/data/task-types')
    if (response.ok) {
      taskTypes.value = await response.json()
    }
  }

  async function fetchOpenProductions() {
    const response = await fetch('/api/data/projects/open')
    if (response.ok) {
      openProductions.value = await response.json()
    }
  }

  async function fetchSequences(productionId) {
    const response = await fetch(
      `/api/data/projects/${productionId}/sequences`
    )
    if (response.ok) {
      sequences.value = await response.json()
    }
  }

  async function fetchEpisodes(productionId) {
    const response = await fetch(
      `/api/data/projects/${productionId}/episodes`
    )
    if (response.ok) {
      episodes.value = await response.json()
    }
  }

  async function fetchAssetTypes(productionId) {
    const response = await fetch(
      `/api/data/projects/${productionId}/asset-types`
    )
    if (response.ok) {
      assetTypes.value = await response.json()
    }
  }

  async function init() {
    await Promise.all([fetchTaskTypes(), fetchOpenProductions()])
  }

  async function setCurrentProduction(productionId) {
    if (!productionId) {
      sequences.value = []
      episodes.value = []
      assetTypes.value = []
      return
    }

    const production = openProductions.value.find(
      (p) => p.id === productionId
    )
    const isTVShow = production?.production_type === 'tvshow'

    if (isTVShow) {
      sequences.value = []
      await Promise.all([
        fetchEpisodes(productionId),
        fetchAssetTypes(productionId),
      ])
    } else {
      episodes.value = []
      await Promise.all([
        fetchSequences(productionId),
        fetchAssetTypes(productionId),
      ])
    }
  }

  return {
    taskTypes,
    openProductions,
    sequences,
    episodes,
    assetTypes,
    fetchTaskTypes,
    fetchOpenProductions,
    fetchSequences,
    fetchEpisodes,
    fetchAssetTypes,
    init,
    setCurrentProduction,
  }
})
