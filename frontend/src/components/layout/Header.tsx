export default function Header() {
  return (
    <header className="border-b-[3px] border-[#111111] bg-[#F4F1EA] sticky top-0 z-50">
      <div className="max-w-[1200px] mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo / Masthead */}
        <a href="/" className="font-masthead text-2xl text-[#111111] tracking-tight">
          OpenSpends<span className="text-[#8C2929]">NG</span>
        </a>

        {/* Navigation — Monospace, Utility-first */}
        <nav className="hidden md:flex gap-0 divide-x divide-[#111111]">
          {[
            { href: '/', label: 'Home' },
            { href: '/projects', label: 'Projects' },
            { href: '/analytics', label: 'Analysis' },
            { href: '/map', label: 'Map' },
          ].map(({ href, label }) => (
            <a
              key={href}
              href={href}
              className="px-4 py-2 text-nav-label text-[#111111] hover:bg-[#E5E0D8] transition-colors"
            >
              {label}
            </a>
          ))}
        </nav>

        {/* Mobile menu */}
        <div className="md:hidden flex items-center gap-2">
          <span className="text-nav-label text-[#747878]">v0.1</span>
        </div>
      </div>

      {/* Ticker Strip */}
      <div className="border-t-[1px] border-b-[1px] border-[#111111] bg-[#111111] text-[#F4F1EA] py-2 overflow-hidden">
        <div className="max-w-[1200px] mx-auto px-4">
          <div className="flex gap-8 text-data-sm items-center">
            <span className="whitespace-nowrap">
              <span className="text-[#BDB8AD]">TRACKED:</span>
              <span className="ml-2 text-[#FCFAF5]">2,847 PROJECTS</span>
            </span>
            <span className="whitespace-nowrap">
              <span className="text-[#BDB8AD]">ALERTS:</span>
              <span className="ml-2 text-[#8C2929]">34 OVER-UTILIZED</span>
            </span>
            <span className="whitespace-nowrap hidden lg:inline">
              <span className="text-[#BDB8AD]">UPDATED:</span>
              <span className="ml-2 text-[#FCFAF5]">2026-05-29 14:30 UTC</span>
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}
