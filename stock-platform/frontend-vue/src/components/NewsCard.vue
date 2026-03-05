<template>
  <a v-if="item.url" :href="item.url" target="_blank" rel="noopener" class="block rounded-lg border border-gray-100 dark:border-gray-600 bg-gray-50/50 dark:bg-surface-elevated p-3 hover:bg-gray-50 dark:hover:bg-gray-600/50 transition-colors">
    <p class="text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-2">{{ item.title || 'No title' }}</p>
    <p class="mt-1 text-xs text-neutral dark:text-gray-400">{{ item.date ? new Date(item.date).toLocaleDateString('ko-KR') : '' }}</p>
  </a>
  <div v-else class="rounded-lg border border-gray-100 dark:border-gray-600 bg-gray-50/50 dark:bg-surface-elevated p-3">
    <p class="text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-2">{{ item.title || 'No title' }}</p>
    <p class="mt-1 text-xs text-neutral dark:text-gray-400">{{ item.date ? new Date(item.date).toLocaleDateString('ko-KR') : '' }}</p>
  </div>
</template>
<script setup>
defineProps({ item: { type: Object, required: true } })
</script>
