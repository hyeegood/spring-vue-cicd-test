<template>
  <div class="inline-flex flex-col items-center rounded-lg bg-gray-50 dark:bg-surface-elevated px-2 py-1">
    <span class="tabular-nums font-semibold" :class="scoreColor">{{ value != null ? Math.round(Number(value)) : '-' }}</span>
    <span v-if="label" class="text-xs text-neutral dark:text-gray-400">{{ label }}</span>
  </div>
</template>
<script setup>
import { computed } from 'vue'
const props = defineProps({ value: Number, label: String, size: String })
const scoreColor = computed(() => {
  const v = props.value
  if (v == null) return 'text-neutral'
  if (v >= 80) return 'text-positive'
  if (v >= 70) return 'text-primary'
  if (v >= 40) return 'text-amber-600'
  return 'text-negative'
})
</script>
