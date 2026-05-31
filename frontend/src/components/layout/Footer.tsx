export default function Footer() {
  return (
    <footer className="border-t-[3px] border-ink-deep bg-cream-page mt-auto">
      <div className="max-w-[1200px] mx-auto px-4 py-6 flex flex-col md:flex-row justify-between items-start gap-4">
        {/* Left: Attribution */}
        <div className="space-y-1">
          <p className="text-label-caps text-ink-deep">
            OpenSpends NG
          </p>
          <p className="text-data-sm text-ink-muted">
            Public budget transparency for Nigerian citizens
          </p>
        </div>

        {/* Center: Data sources */}
        <div className="text-data-sm text-ink-muted">
          Data sourced from official government portals and civic tech APIs
        </div>

        {/* Right: Links */}
        <div className="flex gap-0 divide-x divide-ink-deep">
          <a
            href="https://github.com/k1ng0mar/openspends-ng"
            className="px-3 text-nav-label text-ink-deep hover:bg-selection transition-colors"
            target="_blank"
            rel="noopener noreferrer"
          >
            GITHUB
          </a>
          <span className="px-3 text-nav-label text-ink-muted">
            MIT LICENSE
          </span>
        </div>
      </div>
    </footer>
  )
}
