export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      {/* Hero */}
      <section className="text-center mb-16">
        <h1 className="text-5xl font-bold tracking-tight mb-4">
          OpenSpends <span className="text-green-600">NG</span>
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Track Nigerian government budget allocation & spending — by arm, ministry, project, and location.
          Built for citizens, built for journalists.
        </p>
        <div className="mt-8 flex gap-4 justify-center">
          <input
            type="text"
            placeholder="Search MDA, project, or LGA…"
            className="w-full max-w-md px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none"
          />
          <button className="px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition">
            Search
          </button>
        </div>
      </section>

      {/* Featured Stats */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
        <StatCard
          title="Federal Budget 2025"
          value="₦54.99 Trillion"
          subtitle="Approved national budget"
        />
        <StatCard
          title="States Tracked"
          value="7"
          subtitle="Full budget & spending data"
        />
        <StatCard
          title="Projects Monitored"
          value="500+"
          subtitle="With GPS coordinates"
        />
      </section>

      {/* Map Preview */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-6">Spending by Location</h2>
        <div className="bg-gray-100 rounded-xl h-96 flex items-center justify-center text-gray-400 border border-gray-200">
          <p className="text-center">
            <span className="block text-4xl mb-2">🗺️</span>
            Mapbox heatmap loading…
          </p>
        </div>
      </section>

      {/* Recent Projects */}
      <section>
        <h2 className="text-2xl font-bold mb-6">Recent Project Updates</h2>
        <div className="text-gray-500 text-center py-8 border border-dashed border-gray-300 rounded-lg">
          Projects will appear here once data is ingested.
        </div>
      </section>
    </div>
  )
}

function StatCard({ title, value, subtitle }: { title: string; value: string; subtitle: string }) {
  return (
    <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
      <div className="text-sm text-gray-500 mb-1">{title}</div>
      <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
      <div className="text-sm text-gray-400">{subtitle}</div>
    </div>
  )
}
