<template>
  <div class="rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-surface p-4 shadow-card">
    <p class="text-sm font-medium text-neutral dark:text-gray-400">{{ title }}</p>
    <p class="mt-1 text-2xl font-semibold text-gray-900 dark:text-gray-100">{{ value }}</p>
    <p v-if="sub" class="mt-0.5 text-xs text-neutral dark:text-gray-400">{{ sub }}</p>
  </div>
</template>
<script setup>
defineProps({ title: String, value: { type: String, default: '-' }, sub: String })
</script>
