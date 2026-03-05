<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">스크리너</h1>
    <div class="flex gap-4">
      <input v-model.number="minScore" type="number" min="0" max="100" class="rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-surface px-2 py-1 w-20 text-gray-900 dark:text-gray-100" />
      <input v-model="sector" type="text" placeholder="섹터" class="rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-surface px-2 py-1 w-32 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400" />
      <button @click="fetch" class="rounded bg-primary px-4 py-2 text-white hover:opacity-90">적용</button>
    </div>
    <div v-if="loading" class="flex min-h-[40vh] items-center justify-center">
      <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
    </div>
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <StockCard v-for="row in items" :key="row.symbol" :item="row" />
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getScreener } from '../services/api'
import StockCard from '../components/StockCard.vue'
const minScore = ref(70)
const sector = ref('')
const loading = ref(true)
const items = ref([])
async function fetch() {
  loading.value = true
  try {
    const data = await getScreener({ min_score: minScore.value || undefined, sector: sector.value || undefined })
    items.value = data.items || []
  } catch (e) {
    items.value = []
  } finally {
    loading.value = false
  }
}
onMounted(fetch)
</script>
