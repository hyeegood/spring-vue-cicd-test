// =======================================
// 라우트: 대시보드, 종목 상세, 랭킹
// =======================================
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('../pages/Dashboard.vue') },
  { path: '/stock/:ticker', name: 'StockDetail', component: () => import('../pages/StockDetail.vue') },
  { path: '/rankings', name: 'Rankings', component: () => import('../pages/Rankings.vue') },
  { path: '/screener', name: 'Screener', component: () => import('../pages/Screener.vue') },
  { path: '/compare', name: 'Comparison', component: () => import('../pages/Comparison.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
