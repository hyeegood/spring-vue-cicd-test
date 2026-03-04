<script setup lang="ts">
import { onMounted, ref } from 'vue'

const message = ref<string>('불러오는 중입니다...')
const error = ref<string | null>(null)

const loadHello = async () => {
  try {
    error.value = null
    const res = await fetch('/api/hello')
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`)
    }
    message.value = await res.text()
  } catch (e: any) {
    error.value = 'API 호출 실패'
    message.value = e?.message ?? String(e)
  }
}

onMounted(loadHello)
</script>

<template>
  <main class="page">
    <section class="card">
      <h1>Fullstack Demo</h1>
      <p class="subtitle">Spring Boot 3 + Vue 3 + Vite</p>

      <button class="reload" type="button" @click="loadHello">
        /api/hello 다시 호출
      </button>

      <div class="result" :class="{ error: error }">
        <h2>응답</h2>
        <p>{{ message }}</p>
        <p v-if="error" class="error-text">{{ error }}</p>
      </div>
    </section>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top left, #e0f2ff, #f9fafb);
  padding: 2rem;
  box-sizing: border-box;
}

.card {
  max-width: 480px;
  width: 100%;
  background: white;
  border-radius: 1.25rem;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
  padding: 2.5rem 2.25rem;
  text-align: center;
}

h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
}

.subtitle {
  margin-top: 0.5rem;
  margin-bottom: 1.75rem;
  color: #6b7280;
  font-size: 0.95rem;
}

.reload {
  border: none;
  border-radius: 999px;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #2563eb, #22c55e);
  color: white;
  font-weight: 600;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: transform 0.1s ease, box-shadow 0.1s ease, filter 0.1s ease;
  box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
}

.reload:hover {
  transform: translateY(-1px);
  filter: brightness(1.03);
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.45);
}

.reload:active {
  transform: translateY(0);
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.35);
}

.result {
  margin-top: 2rem;
  padding: 1.25rem 1rem;
  border-radius: 0.85rem;
  background: #f9fafb;
  text-align: left;
  border: 1px solid #e5e7eb;
}

.result h2 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.result p {
  margin: 0.1rem 0;
  font-size: 0.95rem;
  color: #374151;
  word-break: break-all;
}

.result.error {
  border-color: #f97373;
  background: #fef2f2;
}

.error-text {
  margin-top: 0.35rem;
  font-size: 0.85rem;
  color: #b91c1c;
}
</style>
