export default function AnalyticsPage() {
  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <div className="mb-2 text-xs font-mono text-accent/60 uppercase tracking-widest">
        Analytics
      </div>
      <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
      <p className="text-gray-400 mb-8">
        Budget vs spending variance, state comparisons, and geographic breakdowns.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[
          { title: 'Budget vs Spending', desc: 'Compare approved budgets to actual expenditure by MDA' },
          { title: 'State Performance', desc: 'Rank states by fiscal transparency and spending efficiency' },
          { title: 'Sector Breakdown', desc: 'Spending distribution across health, education, infrastructure, etc.' },
          { title: 'Timeline Trends', desc: 'Track budget allocation and spending over 2020–2026' },
        ].map((card) => (
          <div
            key={card.title}
            className="bg-dark-800 border border-dark-600 rounded-xl p-6 hover:border-accent/20 transition-colors"
          >
            <h3 className="text-sm font-semibold text-white mb-1">{card.title}</h3>
            <p className="text-xs text-gray-500 mb-4">{card.desc}</p>
            <div className="h-32 bg-dark-900 rounded-lg flex items-center justify-center">
              <p className="text-xs text-gray-600">Chart placeholder</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
