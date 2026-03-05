<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">종목 비교</h1>
    <p class="text-neutral dark:text-gray-400">추천 종목을 불러와 비교할 수 있습니다.</p>
    <div v-if="loading" class="flex min-h-[40vh] items-center justify-center">
      <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
    </div>
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <StockCard v-for="item in list" :key="item.symbol" :item="item" />
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getRecommendations } from '../services/api'
import StockCard from '../components/StockCard.vue'
const loading = ref(true)
const list = ref([])
onMounted(async () => {
  try {
    list.value = await getRecommendations(30)
  } catch (e) {
    list.value = []
  } finally {
    loading.value = false
  }
})
</script>
