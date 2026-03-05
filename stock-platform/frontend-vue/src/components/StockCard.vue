<template>
  <router-link :to="`/stock/${item.symbol || item.ticker}`" class="block rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-surface p-4 shadow-card hover:border-primary/30 dark:hover:border-primary/50 transition-colors">
    <div class="flex justify-between">
      <div>
        <p class="font-semibold text-gray-900 dark:text-gray-100">{{ item.name || item.company_name || item.ticker }}</p>
        <p class="text-sm text-neutral dark:text-gray-400">{{ item.name_ko || item.company_name_ko || item.ticker }}</p>
      </div>
      <ScoreWidget :value="item.investment_score ?? item.score" label="투자점수" size="sm" />
    </div>
    <div class="mt-3 flex gap-3 text-sm text-neutral dark:text-gray-400">
      <span>{{ item.sector || '-' }}</span>
      <span v-if="item.current_price != null">${{ Number(item.current_price).toFixed(2) }}</span>
    </div>
  </router-link>
</template>
<script setup>
import ScoreWidget from './ScoreWidget.vue'
defineProps({ item: { type: Object, required: true } })
</script>
