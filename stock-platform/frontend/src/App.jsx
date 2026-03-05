import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { DashboardProvider } from './context/DashboardContext'
import AppShell from './components/layout/AppShell'
import Dashboard from './pages/Dashboard'
import StockDetail from './pages/StockDetail'
import Portfolio from './pages/Portfolio'
import Backtest from './pages/Backtest'
import Rankings from './pages/Rankings'
import './index.css'

export default function App() {
  return (
    <DashboardProvider>
      <BrowserRouter>
        <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/stock/:ticker" element={<StockDetail />} />
          <Route path="/rankings" element={<Rankings />} />
          <Route path="/portfolio" element={<Portfolio />} />
          <Route path="/backtest" element={<Backtest />} />
        </Route>
      </Routes>
    </BrowserRouter>
    </DashboardProvider>
  )
}
