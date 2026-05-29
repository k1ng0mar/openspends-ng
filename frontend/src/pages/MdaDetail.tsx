export default function MdaDetailPage() {
  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <div className="mb-2 text-xs font-mono text-accent/60 uppercase tracking-widest">
        Ministry / Department / Agency
      </div>
      <h1 className="text-3xl font-bold text-white mb-2">MDA Detail</h1>
      <p className="text-gray-400 mb-8">
        Budget allocation, spending breakdown, and capital projects.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 bg-dark-800 border border-dark-600 rounded-xl p-6">
          <h2 className="text-sm font-semibold text-white mb-4">Budget vs Spending</h2>
          <div className="h-48 bg-dark-900 rounded-lg flex items-center justify-center">
            <p className="text-xs text-gray-600">D3.js chart placeholder</p>
          </div>
        </div>
        <div className="bg-dark-800 border border-dark-600 rounded-xl p-6">
          <h2 className="text-sm font-semibold text-white mb-4">Quick Stats</h2>
          <div className="space-y-3">
            {[
              { label: 'Approved', value: '—' },
              { label: 'Released', value: '—' },
              { label: 'Spent', value: '—' },
              { label: 'Projects', value: '—' },
            ].map((s) => (
              <div key={s.label} className="flex justify-between text-sm">
                <span className="text-gray-400">{s.label}</span>
                <span className="text-white font-mono">{s.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
