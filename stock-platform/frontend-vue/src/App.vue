<template>
  <div class="min-h-screen bg-background dark:bg-dark-bg transition-colors duration-200">
    <header class="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-dark-card shadow-card dark:shadow-dark-card transition-colors duration-200">
      <div class="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
        <router-link to="/" class="text-xl font-semibold text-primary">Stock Analytics</router-link>
        <nav class="flex items-center gap-6">
          <router-link to="/" class="text-neutral dark:text-gray-300 hover:text-primary dark:hover:text-blue-400">대시보드</router-link>
          <router-link to="/screener" class="text-neutral dark:text-gray-300 hover:text-primary dark:hover:text-blue-400">스크리너</router-link>
          <router-link to="/rankings" class="text-neutral dark:text-gray-300 hover:text-primary dark:hover:text-blue-400">랭킹</router-link>
          <router-link to="/compare" class="text-neutral dark:text-gray-300 hover:text-primary dark:hover:text-blue-400">비교</router-link>
          <button
            type="button"
            :aria-label="isDark ? '라이트 모드로 전환' : '다크 모드로 전환'"
            class="rounded-lg p-2 text-neutral hover:bg-gray-100 dark:hover:bg-gray-700 dark:text-gray-300 transition-colors"
            @click="toggle"
          >
            <span v-if="isDark" class="text-lg">☀️</span>
            <span v-else class="text-lg">🌙</span>
          </button>
        </nav>
      </div>
    </header>
    <main class="mx-auto max-w-7xl px-4 py-6">
      <router-view v-slot="{ Component }">
        <Suspense>
          <component :is="Component" />
          <template #fallback>
            <div class="flex min-h-[40vh] items-center justify-center">
              <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          </template>
        </Suspense>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { useTheme } from './composables/useTheme'

const { isDark, toggle } = useTheme()
</script>
