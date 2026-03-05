<template>
  <div class="space-y-6" v-if="data">
    <!-- Company header: Ticker, Name, Sector -->
    <header class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 transition-colors">{{ data.stock?.company_name }} ({{ data.stock?.ticker }})</h1>
        <p class="text-neutral dark:text-gray-400 mt-0.5">{{ data.stock?.company_name_ko }}</p>
        <span v-if="data.stock?.sector" class="inline-block mt-2 rounded-full bg-accent/20 px-3 py-0.5 text-sm text-accent">{{ data.stock.sector }}</span>
      </div>
      <ScoreWidget :value="data.investment_score ?? data.score_breakdown?.total" :label="data.investment_interpretation || 'Score'" />
    </header>

    <!-- Metrics grid: PE, PBR, ROE, Revenue growth -->
    <section>
      <h2 class="mb-3 text-sm font-medium text-neutral dark:text-gray-400">핵심 지표</h2>
      <div class="grid gap-4 md:grid-cols-4">
        <MetricCard title="Price" :value="latestPrice" />
        <MetricCard title="PER" :value="data.financials?.per != null ? String(data.financials.per) : '-'" />
        <MetricCard title="PBR" :value="data.financials?.pbr != null ? String(data.financials.pbr) : '-'" />
        <MetricCard title="ROE" :value="data.financials?.roe != null ? String(data.financials.roe) + '%' : '-'" />
        <MetricCard title="Revenue growth" :value="data.financials?.revenue_growth != null ? String(data.financials.revenue_growth) + '%' : '-'" />
        <MetricCard title="Risk" :value="data.reliability_analysis?.reliability_level || '-'" />
      </div>
    </section>

    <!-- Price chart -->
    <section>
      <ChartWidget title="Price Chart" :data="data.price_history || []" />
    </section>

    <!-- Quantitative scores: Value, Growth, Quality, Sentiment, Risk, Investment -->
    <section v-if="data.score_breakdown || data.investment_score != null">
      <h2 class="mb-3 text-sm font-medium text-neutral dark:text-gray-400">정량 점수</h2>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
        <div class="rounded-lg bg-white dark:bg-dark-card p-3 shadow-card dark:shadow-dark-card border border-gray-100 dark:border-gray-700 transition-all hover:shadow-card-hover">
          <p class="text-xs text-neutral dark:text-gray-400">Value</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ data.score_breakdown?.value_score ?? '-' }}</p>
        </div>
        <div class="rounded-lg bg-white dark:bg-dark-card p-3 shadow-card dark:shadow-dark-card border border-gray-100 dark:border-gray-700 transition-all hover:shadow-card-hover">
          <p class="text-xs text-neutral dark:text-gray-400">Growth</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ data.score_breakdown?.growth_score ?? '-' }}</p>
        </div>
        <div class="rounded-lg bg-white dark:bg-dark-card p-3 shadow-card dark:shadow-dark-card border border-gray-100 dark:border-gray-700 transition-all hover:shadow-card-hover">
          <p class="text-xs text-neutral dark:text-gray-400">Quality</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ data.score_breakdown?.quality_score ?? '-' }}</p>
        </div>
        <div class="rounded-lg bg-white dark:bg-dark-card p-3 shadow-card dark:shadow-dark-card border border-gray-100 dark:border-gray-700 transition-all hover:shadow-card-hover">
          <p class="text-xs text-neutral dark:text-gray-400">Sentiment</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ data.score_breakdown?.sentiment_score ?? '-' }}</p>
        </div>
        <div class="rounded-lg bg-white dark:bg-dark-card p-3 shadow-card dark:shadow-dark-card border border-gray-100 dark:border-gray-700 transition-all hover:shadow-card-hover">
          <p class="text-xs text-neutral dark:text-gray-400">Risk</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ data.reliability_analysis?.reliability_level ?? '-' }}</p>
        </div>
        <div class="rounded-lg bg-accent/10 dark:bg-accent/20 p-3 border border-accent/30 transition-all hover:shadow-card-hover">
          <p class="text-xs text-accent">Investment</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ data.investment_score ?? '-' }}</p>
        </div>
      </div>
    </section>

    <!-- Glassdoor rating -->
    <section v-if="data.stock?.glassdoor_rating != null || data.stock?.ceo_approval != null" class="rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-dark-card p-4 shadow-card dark:shadow-dark-card transition-all hover:shadow-card-hover">
      <h2 class="text-sm font-medium text-neutral dark:text-gray-400 mb-2">Glassdoor 평점</h2>
      <div class="flex gap-6">
        <div><span class="text-2xl font-semibold text-gray-900 dark:text-gray-100">{{ data.stock?.glassdoor_rating ?? '-' }}</span><span class="text-sm text-neutral dark:text-gray-400 ml-1">/ 5</span></div>
        <div><span class="text-sm text-neutral dark:text-gray-400">CEO 승인</span> <span class="font-medium text-gray-900 dark:text-gray-100">{{ data.stock?.ceo_approval ?? '-' }}</span></div>
      </div>
    </section>

    <!-- AI analysis + label -->
    <div v-if="data.ai_insight" class="rounded-xl border border-primary/20 dark:border-accent/30 bg-primary/5 dark:bg-accent/10 p-4 transition-all hover:shadow-card-hover">
      <div class="flex items-center gap-2 mb-1">
        <p class="text-sm font-medium text-primary dark:text-accent">AI Analysis</p>
        <span :class="['rounded px-2 py-0.5 text-xs font-medium', aiLabelClass]">{{ aiLabelText }}</span>
      </div>
      <p class="mt-1 text-gray-700 dark:text-gray-300">{{ data.ai_insight }}</p>
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <RecommendationCard :recommendation="data.recommendation" :interpretation="data.investment_interpretation" />
      <div class="rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-dark-card p-4 shadow-card dark:shadow-dark-card transition-all hover:shadow-card-hover">
        <p class="text-sm font-medium text-neutral dark:text-gray-400">Reliability</p>
        <p class="mt-1 text-gray-900 dark:text-gray-200">Sector {{ data.reliability_analysis?.sector_reliability ?? '-' }} / Stock {{ data.reliability_analysis?.stock_reliability ?? '-' }}</p>
        <p class="mt-2 text-sm text-neutral dark:text-gray-400">{{ data.reliability_analysis?.interpretation }}</p>
      </div>
    </div>

    <section>
      <h2 class="mb-3 text-lg font-medium text-gray-900 dark:text-gray-100">News</h2>
      <div class="grid gap-2 sm:grid-cols-2">
        <NewsCard v-for="(n, i) in data.news || []" :key="i" :item="n" />
      </div>
    </section>
  </div>
  <div v-else-if="loading" class="space-y-6">
    <div class="h-8 w-48 rounded bg-gray-200 dark:bg-surface-elevated animate-pulse" />
    <div class="grid gap-4 md:grid-cols-4">
      <div v-for="i in 4" :key="i" class="h-20 rounded-xl bg-gray-200 dark:bg-surface-elevated animate-pulse" />
    </div>
    <div class="h-64 rounded-xl bg-gray-200 dark:bg-surface-elevated animate-pulse" />
    <div class="h-24 rounded-xl bg-gray-200 dark:bg-surface-elevated animate-pulse" />
  </div>
  <div v-else class="text-negative">Failed to load.</div>
</template>
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getStockDetail } from '../services/api'
import ScoreWidget from '../components/ScoreWidget.vue'
import MetricCard from '../components/MetricCard.vue'
import ChartWidget from '../components/ChartWidget.vue'
import RecommendationCard from '../components/RecommendationCard.vue'
import NewsCard from '../components/NewsCard.vue'
const route = useRoute()
const loading = ref(true)
const data = ref(null)
const latestPrice = computed(() => {
  const ph = data.value?.price_history
  if (!ph?.length) return '-'
  const v = ph[0]?.close ?? ph[0]?.value
  return v != null ? '$' + Number(v).toFixed(2) : '-'
})
const aiLabelText = computed(() => {
  const l = data.value?.ai_insight_label || 'neutral'
  return l.charAt(0).toUpperCase() + l.slice(1)
})
const aiLabelClass = computed(() => {
  const l = data.value?.ai_insight_label || 'neutral'
  if (l === 'bullish') return 'bg-positive/20 text-positive'
  if (l === 'bearish') return 'bg-negative/20 text-negative'
  return 'bg-gray-200 dark:bg-surface-elevated text-neutral dark:text-gray-400'
})
async function load() {
  const ticker = route.params.ticker
  if (!ticker) return
  loading.value = true
  try { data.value = await getStockDetail(ticker) } catch (e) { data.value = null }
  finally { loading.value = false }
}
onMounted(load)
watch(() => route.params.ticker, load)
</script>
