export default function Header() {
  return (
    <header className="border-b border-dark-700 bg-dark-950/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        {/* Logo */}
        <a href="/" className="text-lg font-bold tracking-tight text-white">
          OpenSpends<span className="text-accent">NG</span>
        </a>

        {/* Nav */}
        <nav className="hidden md:flex gap-6 text-sm text-gray-400">
          <a href="/" className="hover:text-white transition-colors">Home</a>
          <a href="/projects" className="hover:text-white transition-colors">Projects</a>
          <a href="/analytics" className="hover:text-white transition-colors">Analytics</a>
          <a href="/map" className="hover:text-white transition-colors">Map</a>
        </nav>

        {/* Status */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
            <span className="text-xs text-gray-500">v0.1.0</span>
          </div>
        </div>
      </div>
    </header>
  )
}
