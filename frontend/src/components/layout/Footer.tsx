export default function Footer() {
  return (
    <footer className="border-t border-dark-700 bg-dark-950 mt-auto">
      <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <p className="text-xs text-gray-500">
          OpenSpends NG — Data sourced from public government portals. Built for transparency.
        </p>
        <div className="flex gap-4 text-xs text-gray-600">
          <span>MIT License</span>
          <a href="https://github.com/k1ng0mar/openspends-ng" className="hover:text-gray-400 transition-colors">
            GitHub
          </a>
        </div>
      </div>
    </footer>
  )
}
