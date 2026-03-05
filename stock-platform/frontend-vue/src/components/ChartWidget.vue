<template>
  <div class="rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-surface p-4 shadow-card">
    <p class="mb-3 text-sm font-medium text-neutral dark:text-gray-400">{{ title }}</p>
    <div ref="chartRef" class="h-64 w-full"></div>
  </div>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue'
import { createChart } from 'lightweight-charts'
import { useTheme } from '../composables/useTheme'

const props = defineProps({ title: { type: String, default: 'Price' }, data: { type: Array, default: () => [] } })
const chartRef = ref(null)
const { isDark } = useTheme()
let chart = null
let series = null

function init() {
  if (!chartRef.value || !props.data.length) return
  if (chart) chart.remove()
  const dark = isDark.value
  chart = createChart(chartRef.value, {
    layout: {
      background: { color: dark ? '#1E293B' : '#fff' },
      textColor: dark ? '#94A3B8' : '#6B7280',
    },
    width: chartRef.value.clientWidth,
    height: 256,
  })
  series = chart.addAreaSeries({ lineColor: '#2563EB', topColor: 'rgba(37,99,235,0.4)', bottomColor: 'rgba(37,99,235,0)' })
  const parsed = props.data.map(d => ({ time: (d.date || d.time || '').slice(0, 10), value: Number(d.close ?? d.value ?? 0) })).filter(d => d.value > 0)
  series.setData(parsed)
  chart.timeScale().fitContent()
}

onMounted(init)
watch(() => props.data, init, { deep: true })
watch(isDark, init)
</script>
