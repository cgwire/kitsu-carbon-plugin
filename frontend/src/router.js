import { createRouter, createWebHistory } from 'vue-router'
import CarbonFootprint from './components/CarbonFootprint.vue'

const routes = [
  {
    path: '/',
    name: 'carbon',
    component: CarbonFootprint,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
