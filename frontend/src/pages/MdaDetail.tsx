import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../lib/api';

interface MDA {
  id: number;
  name: string;
  code: string;
  level: string;
}

interface Project {
  id: number;
  title: string;
  budget_allocated: number;
  spent: number;
  state: string;
  status: string;
}

export default function MdaDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [mda, setMda] = useState<MDA | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [mdaRes, projRes] = await Promise.all([
          api.get(`/mdas/${id}`),
          api.get(`/projects?mda_id=${id}`),
        ]);
        setMda(mdaRes.data);
        setProjects(projRes.data || []);
      } catch (err) {
        console.error('Failed to load MDA data:', err);
      } finally {
        setLoading(false);
      }
    }
    if (id) loadData();
  }, [id]);

  const formatNaira = (amount: number) => {
    if (amount >= 1e12) return `₦${(amount / 1e12).toFixed(1)}T`;
    if (amount >= 1e9) return `₦${(amount / 1e9).toFixed(1)}B`;
    if (amount >= 1e6) return `₦${(amount / 1e6).toFixed(1)}M`;
    return `₦${amount.toLocaleString()}`;
  };

  const totalAllocated = projects.reduce((acc, p) => acc + (p.budget_allocated || 0), 0);
  const totalSpent = projects.reduce((acc, p) => acc + (p.spent || 0), 0);
  const overCount = projects.filter(p => (p.spent || 0) > (p.budget_allocated || 0) * 1.1).length;

  return (
    <div className="min-h-screen bg-cream-page">
      {/* Header */}
      <section className="border-b-[3px] border-ink-deep bg-ink-deep py-8">
        <div className="max-w-[1200px] mx-auto px-4">
          <div className="text-label-caps text-ink-faint mb-2">MINISTRY / DEPARTMENT / AGENCY</div>
          <h1 className="font-masthead text-3xl text-ivory-surface">
            {loading ? 'Loading...' : mda?.name || 'Unknown MDA'}
          </h1>
          <div className="flex gap-4 mt-2 text-data-sm text-ink-faint">
            <span>Code: {mda?.code || '—'}</span>
            <span>·</span>
            <span>Level: {mda?.level || '—'}</span>
          </div>
        </div>
      </section>

      {loading ? (
        <div className="text-center py-16">
          <div className="text-data-lg text-ink-deep">Loading MDA data...</div>
        </div>
      ) : (
        <>
          {/* Quick Stats */}
          <section className="border-b border-ink-deep bg-ivory-surface">
            <div className="max-w-[1200px] mx-auto px-4 py-8">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-0 divide-x divide-y md:divide-y-0 divide-ink-deep">
                <div className="p-6">
                  <div className="text-label-caps text-ink-muted mb-2">Projects</div>
                  <div className="text-data-lg text-ink-deep">{projects.length}</div>
                </div>
                <div className="p-6">
                  <div className="text-label-caps text-ink-muted mb-2">Allocated</div>
                  <div className="text-data-lg text-ink-deep">{formatNaira(totalAllocated)}</div>
                </div>
                <div className="p-6">
                  <div className="text-label-caps text-ink-muted mb-2">Spent</div>
                  <div className="text-data-lg text-ink-deep">{formatNaira(totalSpent)}</div>
                </div>
                <div className="p-6">
                  <div className="text-label-caps text-ink-muted mb-2">Over-Utilized</div>
                  <div className="text-data-lg text-oxblood">{overCount}</div>
                </div>
              </div>
            </div>
          </section>

          {/* Project Ledger */}
          <section className="max-w-[1200px] mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-masthead text-xl text-ink-deep">Project Ledger</h2>
              <div className="flex gap-0 divide-x divide-ink-deep">
                <button className="px-4 py-2 text-nav-label text-ink-deep hover:bg-selection transition-colors">
                  EXPORT CSV
                </button>
                <button className="px-4 py-2 text-nav-label text-ink-deep hover:bg-selection transition-colors">
                  EXPORT JSON
                </button>
              </div>
            </div>

            {projects.length === 0 ? (
              <div className="text-center py-12 border border-ink-deep bg-ivory-surface">
                <div className="text-data-sm text-ink-muted">No projects found for this MDA</div>
              </div>
            ) : (
              <div className="border border-ink-deep bg-ivory-surface overflow-x-auto">
                <table className="w-full text-left text-data-sm zebra-stripe">
                  <thead>
                    <tr className="border-b-[3px] border-ink-deep bg-cream-page">
                      <th className="py-3 px-4 text-label-caps text-ink-deep font-normal">Project</th>
                      <th className="py-3 px-4 text-label-caps text-ink-deep font-normal">State</th>
                      <th className="py-3 px-4 text-label-caps text-ink-deep font-normal text-right">Allocated</th>
                      <th className="py-3 px-4 text-label-caps text-ink-deep font-normal text-right">Spent</th>
                      <th className="py-3 px-4 text-label-caps text-ink-deep font-normal text-right">Variance</th>
                      <th className="py-3 px-4 text-label-caps text-ink-deep font-normal text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {projects.map((p) => {
                      const v = p.budget_allocated > 0
                        ? ((p.spent - p.budget_allocated) / p.budget_allocated * 100).toFixed(1)
                        : '0.0';
                      const isOver = parseFloat(v) > 0;
                      
                      return (
                        <tr key={p.id} className="border-b border-selection hover:bg-selection">
                          <td className="py-3 px-4 text-ink-deep">{p.title || `Project ${p.id}`}</td>
                          <td className="py-3 px-4 text-ink-muted">{p.state || 'N/A'}</td>
                          <td className="py-3 px-4 text-right font-mono">{formatNaira(p.budget_allocated || 0)}</td>
                          <td className="py-3 px-4 text-right font-mono">{formatNaira(p.spent || 0)}</td>
                          <td className={`py-3 px-4 text-right font-mono ${isOver ? 'text-oxblood' : 'text-forest'}`}>
                            {isOver ? '+' : ''}{v}%
                          </td>
                          <td className={`py-3 px-4 text-center font-mono ${isOver ? 'text-oxblood' : 'text-forest'}`}>
                            {isOver ? 'OVER' : 'OK'}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
