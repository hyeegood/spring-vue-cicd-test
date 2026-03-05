import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import SearchBar from '../ui/SearchBar'

export default function AppShell() {
  return (
    <div className="min-h-screen bg-surface">
      <Sidebar />
      <div className="pl-56">
        <header className="sticky top-0 z-20 flex h-14 items-center gap-4 border-b border-surface-border bg-white/95 px-6 backdrop-blur">
          <SearchBar className="flex-1" />
        </header>
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
