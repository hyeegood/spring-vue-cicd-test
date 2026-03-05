import { ref, onMounted, watch } from 'vue'

const STORAGE_KEY = 'stock-analytics-theme'
const isDark = ref(true) // 기본값: 다크(프로페셔널 핀테크 테마)
let initialized = false

function init() {
  if (typeof document === 'undefined') return
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved === 'dark') isDark.value = true
    else if (saved === 'light') isDark.value = false
    else isDark.value = true // 저장값 없으면 다크 기본
  } catch (_) {
    isDark.value = true
  }
  document.documentElement.classList.toggle('dark', isDark.value)
}

export function useTheme() {
  function apply(isDarkMode) {
    if (typeof document === 'undefined') return
    if (isDarkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  function toggle() {
    isDark.value = !isDark.value
    try {
      localStorage.setItem(STORAGE_KEY, isDark.value ? 'dark' : 'light')
    } catch (_) {}
    apply(isDark.value)
  }

  if (!initialized && typeof document !== 'undefined') {
    initialized = true
    init()
  }

  onMounted(() => {
    if (!initialized) {
      initialized = true
      init()
    }
  })

  watch(isDark, (v) => apply(v), { flush: 'post' })

  return { isDark, toggle, apply }
}
