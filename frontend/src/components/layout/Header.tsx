export default function Header() {
  return (
    <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <a href="/" className="text-xl font-bold tracking-tight">
          OpenSpends<span className="text-green-600">NG</span>
        </a>

        {/* Nav */}
        <nav className="flex gap-6 text-sm font-medium text-gray-600">
          <a href="/" className="hover:text-gray-900 transition">Home</a>
          <a href="/projects" className="hover:text-gray-900 transition">Projects</a>
          <a href="/analytics" className="hover:text-gray-900 transition">Analytics</a>
          <a href="/map" className="hover:text-gray-900 transition">Map</a>
        </nav>

        {/* Meta */}
        <div className="text-xs text-gray-400">
          v0.1.0
        </div>
      </div>
    </header>
  )
}
