<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">랭킹</h1>
    <div class="flex gap-2">
      <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id" class="rounded-lg px-4 py-2 text-sm font-medium transition-colors" :class="activeTab === tab.id ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-surface-elevated text-neutral dark:text-gray-300'">{{ tab.label }}</button>
    </div>
    <div v-if="loading" class="flex min-h-[40vh] items-center justify-center">
      <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
    </div>
    <div v-else class="overflow-x-auto">
      <table class="w-full border-collapse">
        <thead>
          <tr class="border-b border-gray-200 dark:border-gray-600 text-left text-sm text-neutral dark:text-gray-400">
            <th class="p-3">순위</th>
            <th class="p-3">티커</th>
            <th class="p-3">회사명</th>
            <th class="p-3 text-right">점수</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in list" :key="row.ticker" class="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-surface-elevated">
            <td class="p-3 text-gray-900 dark:text-gray-200">{{ i + 1 }}</td>
            <td class="p-3"><router-link :to="`/stock/${row.ticker}`" class="font-medium text-primary">{{ row.ticker }}</router-link></td>
            <td class="p-3 text-gray-900 dark:text-gray-200">{{ row.company_name }} <span v-if="row.company_name_ko" class="text-neutral dark:text-gray-400">({{ row.company_name_ko }})</span></td>
            <td class="p-3 text-right font-medium text-gray-900 dark:text-gray-200">{{ row.score != null ? Math.round(row.score) : '–' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getRankings } from '../services/api'

const tabs = [{ id: 'score', label: '투자점수' }, { id: 'value', label: '밸류' }, { id: 'growth', label: '성장' }]
const activeTab = ref('score')
const loading = ref(true)
const list = ref([])

async function fetchList() {
  loading.value = true
  try {
    list.value = await getRankings(activeTab.value, 50)
  } catch (e) {
    list.value = []
  } finally {
    loading.value = false
  }
}
onMounted(fetchList)
watch(activeTab, fetchList)
</script>
