import { useState, useEffect } from 'react';
import { fetchProjects, type Project } from '../lib/api';

export default function ProjectListPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'over' | 'under'>('all');

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchProjects();
        setProjects(data);
      } catch (err) {
        console.error('Failed to load projects:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const formatNaira = (amount: number) => {
    if (amount >= 1e12) return `₦${(amount / 1e12).toFixed(1)}T`;
    if (amount >= 1e9) return `₦${(amount / 1e9).toFixed(1)}B`;
    if (amount >= 1e6) return `₦${(amount / 1e6).toFixed(1)}M`;
    return `₦${amount.toLocaleString()}`;
  };

  const filteredProjects = projects.filter(p => {
    if (filter === 'all') return true;
    const isOver = (p.spent || 0) > (p.budget_allocated || 0) * 1.1;
    return filter === 'over' ? isOver : !isOver;
  });

  return (
    <div className="min-h-screen bg-cream-page">
      {/* Header */}
      <section className="border-b-[3px] border-ink-deep bg-ink-deep py-8">
        <div className="max-w-[1200px] mx-auto px-4">
          <div className="text-label-caps text-ink-faint mb-2">PROJECT REGISTRY</div>
          <h1 className="font-masthead text-3xl text-ivory-surface">Capital Projects</h1>
          <p className="text-ink-faint mt-2">
            Browse all tracked government projects by state, ministry, and budget status.
          </p>
        </div>
      </section>

      {/* Filters */}
      <section className="border-b border-ink-deep bg-ivory-surface">
        <div className="max-w-[1200px] mx-auto px-4 py-4">
          <div className="flex gap-0 divide-x divide-ink-deep">
            {['all', 'over', 'under'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f as 'all' | 'over' | 'under')}
                className={`px-4 py-2 text-nav-label transition-colors ${
                  filter === f
                    ? 'bg-ink-deep text-ivory-surface'
                    : 'bg-transparent text-ink-deep hover:bg-selection'
                }`}
              >
                {f === 'all' ? 'ALL' : f === 'over' ? 'OVER-UTILIZED' : 'ON TRACK'}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Results */}
      <section className="max-w-[1200px] mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center py-16">
            <div className="text-data-lg text-ink-deep">Loading project data...</div>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="text-center py-16 border border-ink-deep bg-ivory-surface">
            <div className="text-data-sm text-ink-muted">No projects found</div>
          </div>
        ) : (
          <>
            <div className="text-data-sm text-ink-muted mb-4">
              Showing {filteredProjects.length} of {projects.length} projects
            </div>
            
            <div className="border border-ink-deep bg-ivory-surface overflow-x-auto">
              <table className="w-full text-left text-data-sm zebra-stripe">
                <thead>
                  <tr className="border-b-[3px] border-ink-deep bg-cream-page">
                    <th className="py-3 px-4 text-label-caps text-ink-deep font-normal">Project ID</th>
                    <th className="py-3 px-4 text-label-caps text-ink-deep font-normal">Title</th>
                    <th className="py-3 px-4 text-label-caps text-ink-deep font-normal">Ministry</th>
                    <th className="py-3 px-4 text-label-caps text-ink-deep font-normal">State</th>
                    <th className="py-3 px-4 text-label-caps text-ink-deep font-normal text-right">Allocated</th>
                    <th className="py-3 px-4 text-label-caps text-ink-deep font-normal text-right">Spent</th>
                    <th className="py-3 px-4 text-label-caps text-ink-deep font-normal text-center">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProjects.map((p) => {
                    const isOver = (p.spent || 0) > (p.budget_allocated || 0) * 1.1;
                    
                    return (
                      <tr key={p.id} className="border-b border-selection hover:bg-selection">
                        <td className="py-3 px-4 font-mono text-ink-muted">{p.id}</td>
                        <td className="py-3 px-4 text-ink-deep">{p.title || 'Untitled'}</td>
                        <td className="py-3 px-4 text-ink-muted">{p.mda_name || 'N/A'}</td>
                        <td className="py-3 px-4 text-ink-muted">{p.state || 'N/A'}</td>
                        <td className="py-3 px-4 text-right font-mono">{formatNaira(p.budget_allocated || 0)}</td>
                        <td className="py-3 px-4 text-right font-mono">{formatNaira(p.spent || 0)}</td>
                        <td className={`py-3 px-4 text-center font-mono ${isOver ? 'text-oxblood' : 'text-forest'}`}>
                          {isOver ? 'OVER' : 'OK'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </>
        )}
      </section>

      {/* Export */}
      <section className="border-t border-ink-deep bg-cream-page py-6">
        <div className="max-w-[1200px] mx-auto px-4 flex gap-0 divide-x divide-ink-deep">
          <button className="px-4 py-2 text-nav-label text-ink-deep hover:bg-selection transition-colors">
            EXPORT CSV
          </button>
          <button className="px-4 py-2 text-nav-label text-ink-deep hover:bg-selection transition-colors">
            EXPORT JSON
          </button>
        </div>
      </section>
    </div>
  );
}
