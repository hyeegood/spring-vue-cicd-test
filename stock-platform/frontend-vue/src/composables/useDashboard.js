import { ref, computed } from 'vue'
import { getDashboardAnalytics } from '../services/api'
const analytics = ref(null)
const loading = ref(false)
const error = ref(null)
export function useDashboard() {
  const topPicks = computed(() => analytics.value?.top_picks ?? [])
  const trendingStocks = computed(() => analytics.value?.trending_stocks ?? [])
  async function fetchDashboard() {
    loading.value = true
    error.value = null
    try {
      analytics.value = await getDashboardAnalytics()
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }
  return { analytics, loading, error, topPicks, trendingStocks, fetchDashboard }
}
