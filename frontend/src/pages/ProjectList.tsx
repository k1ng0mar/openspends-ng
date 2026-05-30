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
    <div className="min-h-screen bg-[#F4F1EA]">
      {/* Header */}
      <section className="border-b-[3px] border-[#111111] bg-[#111111] py-8">
        <div className="max-w-[1200px] mx-auto px-4">
          <div className="text-label-caps text-[#BDB8AD] mb-2">PROJECT REGISTRY</div>
          <h1 className="font-masthead text-3xl text-[#FCFAF5]">Capital Projects</h1>
          <p className="text-[#BDB8AD] mt-2">
            Browse all tracked government projects by state, ministry, and budget status.
          </p>
        </div>
      </section>

      {/* Filters */}
      <section className="border-b border-[#111111] bg-[#FCFAF5]">
        <div className="max-w-[1200px] mx-auto px-4 py-4">
          <div className="flex gap-0 divide-x divide-[#111111]">
            {['all', 'over', 'under'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f as 'all' | 'over' | 'under')}
                className={`px-4 py-2 text-nav-label transition-colors ${
                  filter === f
                    ? 'bg-[#111111] text-[#FCFAF5]'
                    : 'bg-transparent text-[#111111] hover:bg-[#E5E0D8]'
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
            <div className="text-data-lg text-[#111111]">Loading project data...</div>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="text-center py-16 border border-[#111111] bg-[#FCFAF5]">
            <div className="text-data-sm text-[#747878]">No projects found</div>
          </div>
        ) : (
          <>
            <div className="text-data-sm text-[#747878] mb-4">
              Showing {filteredProjects.length} of {projects.length} projects
            </div>
            
            <div className="border border-[#111111] bg-[#FCFAF5] overflow-x-auto">
              <table className="w-full text-left text-data-sm zebra-stripe">
                <thead>
                  <tr className="border-b-[3px] border-[#111111] bg-[#F4F1EA]">
                    <th className="py-3 px-4 text-label-caps text-[#111111] font-normal">Project ID</th>
                    <th className="py-3 px-4 text-label-caps text-[#111111] font-normal">Title</th>
                    <th className="py-3 px-4 text-label-caps text-[#111111] font-normal">Ministry</th>
                    <th className="py-3 px-4 text-label-caps text-[#111111] font-normal">State</th>
                    <th className="py-3 px-4 text-label-caps text-[#111111] font-normal text-right">Allocated</th>
                    <th className="py-3 px-4 text-label-caps text-[#111111] font-normal text-right">Spent</th>
                    <th className="py-3 px-4 text-label-caps text-[#111111] font-normal text-center">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProjects.map((p) => {
                    const isOver = (p.spent || 0) > (p.budget_allocated || 0) * 1.1;
                    
                    return (
                      <tr key={p.id} className="border-b border-[#E5E0D8] hover:bg-[#E5E0D8]">
                        <td className="py-3 px-4 font-mono text-[#747878]">{p.id}</td>
                        <td className="py-3 px-4 text-[#111111]">{p.title || 'Untitled'}</td>
                        <td className="py-3 px-4 text-[#747878]">{p.mda_name || 'N/A'}</td>
                        <td className="py-3 px-4 text-[#747878]">{p.state || 'N/A'}</td>
                        <td className="py-3 px-4 text-right font-mono">{formatNaira(p.budget_allocated || 0)}</td>
                        <td className="py-3 px-4 text-right font-mono">{formatNaira(p.spent || 0)}</td>
                        <td className={`py-3 px-4 text-center font-mono ${isOver ? 'text-[#8C2929]' : 'text-[#2D5D40]'}`}>
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
      <section className="border-t border-[#111111] bg-[#F4F1EA] py-6">
        <div className="max-w-[1200px] mx-auto px-4 flex gap-0 divide-x divide-[#111111]">
          <button className="px-4 py-2 text-nav-label text-[#111111] hover:bg-[#E5E0D8] transition-colors">
            EXPORT CSV
          </button>
          <button className="px-4 py-2 text-nav-label text-[#111111] hover:bg-[#E5E0D8] transition-colors">
            EXPORT JSON
          </button>
        </div>
      </section>
    </div>
  );
}
