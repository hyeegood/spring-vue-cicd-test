import { ref, computed } from 'vue'
import { getDashboardAnalytics } from '../services/api'
const state = ref({ analytics: null, loading: false, error: null })
export function useDashboardStore() {
  const analytics = computed(() => state.value.analytics)
  const loading = computed(() => state.value.loading)
  async function load() {
    state.value.loading = true
    state.value.error = null
    try {
      state.value.analytics = await getDashboardAnalytics()
    } catch (e) {
      state.value.error = e.message
    } finally {
      state.value.loading = false
    }
  }
  return { analytics, loading, load }
}
