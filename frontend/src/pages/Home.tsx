import { useState } from 'react'

export default function HomePage() {
  const [query, setQuery] = useState('')

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">

      {/* ── Hero ── */}
      <section className="mb-14">
        <div className="mb-2 text-xs font-mono text-accent/60 uppercase tracking-widest">
          Nigeria Budget Explorer
        </div>
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-3">
          OpenSpends <span className="text-accent">NG</span>
        </h1>
        <p className="text-base text-gray-400 max-w-2xl mb-8">
          Track federal, state & local government budget allocation and spending —
          per ministry, project, and GPS location. Built for citizens. Built for journalists.
        </p>

        {/* Search */}
        <div className="flex gap-3 max-w-lg">
          <div className="flex-1 relative">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search MDA, project, or LGA…"
              className="w-full pl-10 pr-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-colors"
            />
          </div>
          <button className="px-5 py-3 bg-accent text-dark-950 rounded-lg font-semibold text-sm hover:bg-accent-dim transition-colors">
            Search
          </button>
        </div>
      </section>

      {/* ── Stats Row ── */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-14">
        <StatCard label="2025 Budget" value="₦54.99T" hint="Approved federal" accent />
        <StatCard label="States Tracked" value="7" hint="Full fiscal data" />
        <StatCard label="Projects" value="500+" hint="With GPS coordinates" />
        <StatCard label="Data Sources" value="12" hint="Govt portals + civic tech" />
      </section>

      {/* ── Main Content Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-14">

        {/* Map Preview */}
        <div className="lg:col-span-2 bg-dark-800 rounded-xl border border-dark-600 overflow-hidden">
          <div className="px-5 py-4 border-b border-dark-700 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Spending by Location</h2>
            <a href="/map" className="text-xs text-accent hover:text-accent-dim transition-colors">
              Full Map →
            </a>
          </div>
          <div className="h-80 bg-dark-900 flex items-center justify-center relative overflow-hidden">
            <div className="absolute inset-0 opacity-5">
              <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5"/>
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid)" />
              </svg>
            </div>
            <div className="text-center z-10">
              <div className="text-5xl mb-3 opacity-30">🗺️</div>
              <p className="text-sm text-gray-500">Mapbox heatmap</p>
              <p className="text-xs text-gray-600 mt-1">Connect MAPBOX_TOKEN to render</p>
            </div>
          </div>
        </div>

        {/* Top Spenders */}
        <div className="bg-dark-800 rounded-xl border border-dark-600">
          <div className="px-5 py-4 border-b border-dark-700">
            <h2 className="text-sm font-semibold text-white">Top MDAs by Budget</h2>
          </div>
          <div className="p-5 space-y-4">
            {[
              { name: 'Finance', amount: '₦5.2T', pct: 100 },
              { name: 'Health', amount: '₦2.1T', pct: 40 },
              { name: 'Education', amount: '₦1.45T', pct: 28 },
              { name: 'Defence', amount: '₦950B', pct: 18 },
              { name: 'Works', amount: '₦1.1T', pct: 21 },
            ].map((mda) => (
              <div key={mda.name}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-300">{mda.name}</span>
                  <span className="text-gray-400 font-mono">{mda.amount}</span>
                </div>
                <div className="h-1.5 bg-dark-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-accent/70 rounded-full transition-all"
                    style={{ width: `${mda.pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Recent Projects ── */}
      <section>
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-sm font-semibold text-white">Recent Project Updates</h2>
          <a href="/projects" className="text-xs text-accent hover:text-accent-dim transition-colors">
            View All →
          </a>
        </div>
        <div className="text-gray-500 text-center py-10 border border-dark-600 rounded-xl text-sm bg-dark-800/50">
          Projects will appear once data is ingested.
        </div>
      </section>

      {/* ── Data Sources ── */}
      <section className="mt-14 pt-10 border-t border-dark-700">
        <h2 className="text-xs font-mono text-gray-500 uppercase tracking-widest mb-4">
          Data Sources
        </h2>
        <div className="flex flex-wrap gap-2">
          {[
            'Budget Office of the Federation',
            'GovSpend.ng (BudgIT)',
            'Tracka.ng (BudgIT)',
            'NGF Public Finance DB',
            'OAGF',
            'BPP / NOCOPO',
            'ICPC',
            'NBS',
          ].map((source) => (
            <span
              key={source}
              className="px-3 py-1.5 bg-dark-800 border border-dark-600 rounded-full text-xs text-gray-400"
            >
              {source}
            </span>
          ))}
        </div>
      </section>
    </div>
  )
}

function StatCard({ label, value, hint, accent }: {
  label: string
  value: string
  hint: string
  accent?: boolean
}) {
  return (
    <div className="bg-dark-800 rounded-xl border border-dark-600 p-5">
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <div className={`text-2xl font-bold font-mono mb-1 ${accent ? 'text-accent' : 'text-white'}`}>
        {value}
      </div>
      <div className="text-xs text-gray-500">{hint}</div>
    </div>
  )
}
