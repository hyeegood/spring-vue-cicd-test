<template>
  <div class="animate-pulse rounded-md bg-gray-200 dark:bg-surface-elevated" :class="[sizeClass]" />
</template>
<script setup>
import { computed } from 'vue'
const props = defineProps({
  type: { type: String, default: 'line' }, // line, card, circle, title
})
const sizeClass = computed(() => {
  switch (props.type) {
    case 'title': return 'h-7 w-48'
    case 'card': return 'h-32 w-full'
    case 'circle': return 'h-10 w-10 rounded-full'
    default: return 'h-4 w-full'
  }
})
</script>
