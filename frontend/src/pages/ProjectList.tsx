export default function ProjectListPage() {
  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <div className="mb-2 text-xs font-mono text-accent/60 uppercase tracking-widest">
        Explore
      </div>
      <h1 className="text-3xl font-bold text-white mb-2">Projects</h1>
      <p className="text-gray-400 mb-8">
        Browse capital projects by state, status, ministry, or budget range.
      </p>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-8">
        {['All States', 'In Progress', 'Completed', 'Abandoned', 'Federal'].map((f) => (
          <button
            key={f}
            className="px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg text-sm text-gray-300 hover:border-accent/30 hover:text-white transition-colors"
          >
            {f}
          </button>
        ))}
      </div>

      {/* Placeholder */}
      <div className="text-gray-500 text-center py-16 border border-dark-600 rounded-xl bg-dark-800/50 text-sm">
        Project data will appear once ingested from Tracka, BPP, and state portals.
      </div>
    </div>
  )
}
