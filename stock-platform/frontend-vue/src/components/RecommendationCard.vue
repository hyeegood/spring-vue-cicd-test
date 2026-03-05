<template>
  <div class="rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-surface p-4 shadow-card">
    <p class="text-sm font-medium text-neutral dark:text-gray-400">투자 의견</p>
    <p class="mt-1 text-lg font-semibold" :class="interpretationClass">{{ interpretation }}</p>
    <dl class="mt-3 space-y-1 text-sm">
      <div v-if="rec.entry_price != null" class="flex justify-between">
        <dt class="text-neutral dark:text-gray-400">진입가</dt>
        <dd class="font-medium dark:text-gray-200">${{ formatNum(rec.entry_price) }}</dd>
      </div>
      <div v-if="rec.stop_loss != null" class="flex justify-between">
        <dt class="text-neutral dark:text-gray-400">손절가</dt>
        <dd class="font-medium text-negative">${{ formatNum(rec.stop_loss) }}</dd>
      </div>
      <div v-if="rec.target_price != null" class="flex justify-between">
        <dt class="text-neutral dark:text-gray-400">목표가</dt>
        <dd class="font-medium text-positive">${{ formatNum(rec.target_price) }}</dd>
      </div>
    </dl>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  recommendation: { type: Object, default: () => ({}) },
  interpretation: { type: String, default: '' },
})

const rec = computed(() => props.recommendation || {})

function formatNum(n) {
  if (n == null) return '–'
  return Number(n).toLocaleString(undefined, { maximumFractionDigits: 2 })
}

const interpretationClass = computed(() => {
  const i = (props.interpretation || '').toLowerCase()
  if (i.includes('strong') || i.includes('buy')) return 'text-positive'
  if (i.includes('buy')) return 'text-primary'
  if (i.includes('avoid') || i.includes('weak')) return 'text-negative'
  return 'text-neutral'
})
</script>
