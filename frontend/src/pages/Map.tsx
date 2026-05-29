export default function MapPage() {
  return (
    <div className="w-full h-screen flex flex-col">
      {/* Top bar */}
      <div className="px-6 py-3 bg-dark-900 border-b border-dark-700 flex items-center justify-between">
        <h1 className="text-sm font-semibold text-white">Nigeria Budget Map</h1>
        <div className="flex gap-2">
          {['Spending', 'Projects', 'States'].map((f) => (
            <button
              key={f}
              className="px-3 py-1.5 bg-dark-800 border border-dark-600 rounded text-xs text-gray-400 hover:text-white transition-colors"
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Map area */}
      <div className="flex-1 bg-dark-950 flex items-center justify-center relative">
        <div className="absolute inset-0 opacity-5">
          <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="mapGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#mapGrid)" />
          </svg>
        </div>
        <div className="text-center z-10">
          <div className="text-6xl mb-4 opacity-20">🗺️</div>
          <p className="text-sm text-gray-500">Interactive Mapbox GL map</p>
          <p className="text-xs text-gray-600 mt-1">
            Connect MAPBOX_TOKEN and load GeoJSON data to render
          </p>
        </div>
      </div>
    </div>
  )
}
