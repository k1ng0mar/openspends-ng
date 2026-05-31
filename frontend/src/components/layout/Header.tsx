import { useState, useEffect } from 'react'
import { fetchProjects, type Project } from '../../lib/api'

export default function Header() {
  const [ticker, setTicker] = useState({ active: 0, over: 0, updated: '' })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProjects().then((data: Project[]) => {
      const overUtilized = data.filter(p => (p.spent || 0) > (p.budget_allocated || 0) * 1.1).length
      setTicker({
        active: data.length,
        over: overUtilized,
        updated: new Date().toISOString().replace('T', ' ').slice(0, 16) + ' UTC',
      })
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  return (
    <header className="border-b-[3px] border-ink-deep bg-cream-page sticky top-0 z-50">
      <div className="max-w-[1200px] mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo / Masthead */}
        <a href="/" className="font-masthead text-2xl text-ink-deep tracking-tight">
          OpenSpends<span className="text-oxblood">NG</span>
        </a>

        {/* Navigation — Monospace, Utility-first */}
        <nav className="hidden md:flex gap-0 divide-x divide-ink-deep">
          {[
            { href: '/', label: 'Home' },
            { href: '/projects', label: 'Projects' },
            { href: '/analytics', label: 'Analysis' },
            { href: '/map', label: 'Map' },
          ].map(({ href, label }) => (
            <a
              key={href}
              href={href}
              className="px-4 py-2 text-nav-label text-ink-deep hover:bg-selection transition-colors"
            >
              {label}
            </a>
          ))}
        </nav>

        {/* Mobile menu spacer */}
        <div className="md:hidden" />
      </div>

      {/* Ticker Strip — Live Data */}
      <div className="border-t-[1px] border-b-[1px] border-ink-deep bg-ink-deep text-cream-page py-2 overflow-hidden">
        <div className="max-w-[1200px] mx-auto px-4">
          <div className="flex gap-8 text-data-sm items-center">
            <span className="whitespace-nowrap">
              <span className="text-ink-faint">TRACKED:</span>
              <span className="ml-2 text-ivory-surface">
                {loading ? '...' : `${ticker.active} PROJECTS`}
              </span>
            </span>
            <span className="whitespace-nowrap">
              <span className="text-ink-faint">ALERTS:</span>
              <span className="ml-2 text-oxblood">
                {loading ? '...' : `${ticker.over} OVER-UTILIZED`}
              </span>
            </span>
            <span className="whitespace-nowrap hidden lg:inline">
              <span className="text-ink-faint">UPDATED:</span>
              <span className="ml-2 text-ivory-surface">
                {loading ? '...' : ticker.updated}
              </span>
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}
