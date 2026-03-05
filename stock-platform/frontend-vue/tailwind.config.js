/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // 프로페셔널 핀테크 (라이트)
        background: '#F7F9FC',
        primary: '#2563EB',
        positive: '#22C55E',
        negative: '#EF4444',
        neutral: '#6B7280',
        // 다크 테마 (Finviz/SeekingAlpha 스타일)
        'dark-bg': '#0B1220',
        'dark-card': '#111827',
        accent: '#3B82F6',
        surface: '#1E293B',
        'surface-elevated': '#334155',
      },
      boxShadow: {
        card: '0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)',
        'card-hover': '0 4px 6px -1px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.06)',
        'dark-card': '0 1px 3px 0 rgb(0 0 0 / 0.3)',
      },
      transitionDuration: { 150: '150ms', 200: '200ms' },
    },
  },
  plugins: [],
}
