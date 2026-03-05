<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">대시보드</h1>
    <section v-if="loading" class="flex min-h-[40vh] items-center justify-center">
      <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
    </section>
    <template v-else>
      <div class="grid gap-4 md:grid-cols-3">
        <MetricCard title="S&P 500" value="-" sub="Market" />
        <MetricCard title="NASDAQ" value="-" sub="Market" />
        <MetricCard title="VIX" value="-" sub="Volatility" />
      </div>
      <section>
        <h2 class="mb-3 text-lg font-medium text-gray-900 dark:text-gray-100">Top 투자 추천</h2>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <StockCard v-for="pick in analytics?.top_picks || []" :key="pick.ticker" :item="pick" />
        </div>
      </section>
      <section>
        <h2 class="mb-3 text-lg font-medium text-gray-900 dark:text-gray-100">트렌딩</h2>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <StockCard v-for="s in (analytics?.trending_stocks || []).slice(0, 6)" :key="s.ticker" :item="s" />
        </div>
      </section>
      <section>
        <h2 class="mb-3 text-lg font-medium text-gray-900 dark:text-gray-100">Top 섹터</h2>
        <div class="flex flex-wrap gap-2">
          <span v-for="sec in analytics?.top_sectors || []" :key="sec.sector" class="rounded-full bg-gray-100 dark:bg-surface-elevated px-3 py-1 text-sm text-gray-800 dark:text-gray-200">{{ sec.sector }} ({{ sec.count }})</span>
        </div>
      </section>
      <section>
        <h2 class="mb-3 text-lg font-medium text-gray-900 dark:text-gray-100">시장 뉴스</h2>
        <div class="grid gap-2 sm:grid-cols-2">
          <NewsCard v-for="(n, i) in analytics?.market_news || []" :key="i" :item="n" />
        </div>
      </section>
    </template>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getDashboardAnalytics } from '../services/api'
import StockCard from '../components/StockCard.vue'
import MetricCard from '../components/MetricCard.vue'
import NewsCard from '../components/NewsCard.vue'
const loading = ref(true)
const analytics = ref(null)
onMounted(async () => {
  try { analytics.value = await getDashboardAnalytics() } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>
