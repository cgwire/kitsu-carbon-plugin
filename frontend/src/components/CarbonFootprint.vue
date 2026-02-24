<template>
  <ProductionFootprint
    v-if="productionId"
    :production-id="productionId"
    :episode-id="episodeId"
  />
  <StudioFootprint v-else />
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useMainStore } from '../stores/main'
import ProductionFootprint from './ProductionFootprint.vue'
import StudioFootprint from './StudioFootprint.vue'

const route = useRoute()
const store = useMainStore()

const productionId = computed(() => route.query.production_id || null)
const episodeId = computed(() => route.query.episode_id || null)

onMounted(() => {
  store.init()
})

watch(productionId, (id) => {
  store.setCurrentProduction(id)
})
</script>
