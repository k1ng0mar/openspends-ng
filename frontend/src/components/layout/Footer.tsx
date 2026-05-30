export default function Footer() {
  return (
    <footer className="border-t-[3px] border-[#111111] bg-[#F4F1EA] mt-auto">
      <div className="max-w-[1200px] mx-auto px-4 py-6 flex flex-col md:flex-row justify-between items-start gap-4">
        {/* Left: Attribution */}
        <div className="space-y-1">
          <p className="text-label-caps text-[#111111]">
            OpenSpends NG
          </p>
          <p className="text-data-sm text-[#747878]">
            Public budget transparency for Nigerian citizens
          </p>
        </div>

        {/* Center: Data sources */}
        <div className="text-data-sm text-[#747878]">
          Data sourced from official government portals and civic tech APIs
        </div>

        {/* Right: Links */}
        <div className="flex gap-0 divide-x divide-[#111111]">
          <a
            href="https://github.com/k1ng0mar/openspends-ng"
            className="px-3 text-nav-label text-[#111111] hover:bg-[#E5E0D8] transition-colors"
            target="_blank"
            rel="noopener noreferrer"
          >
            GITHUB
          </a>
          <span className="px-3 text-nav-label text-[#747878]">
            MIT LICENSE
          </span>
        </div>
      </div>
    </footer>
  )
}
