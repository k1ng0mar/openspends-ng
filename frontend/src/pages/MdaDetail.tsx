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
    <div className="min-h-screen bg-[#F4F1EA]">
      {/* Header */}
      <section className="border-b-[3px] border-[#111111] bg-[#111111] py-8">
        <div className="max-w-[1200px] mx-auto px-4">
          <div className="text-label-caps text-[#BDB8AD] mb-2">MINISTRY / DEPARTMENT / AGENCY</div>
          <h1 className="font-masthead text-3xl text-[#FCFAF5]">
            {loading ? 'Loading...' : mda?.name || 'Unknown MDA'}
          </h1>
          <div className="flex gap-4 mt-2 text-data-sm text-[#BDB8AD]">
            <span>Code: {mda?.code || '—'}</span>
            <span>·</span>
            <span>Level: {mda?.level || '—'}</span>
          </div>
        </div>
      </section>

      {loading ? (
        <div className="text-center py-16">
          <div className="text-data-lg text-[#111111]">Loading MDA data...</div>
        </div>
      ) : (
        <>
          {/* Quick Stats */}
          <section className="border-b border-[#111111] bg-[#FCFAF5]">
            <div className="max-w-[1200px] mx-auto px-4 py-8">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-0 divide-x divide-y md:divide-y-0 divide-[#111111]">
                <div className="p-6">
                  <div className="text-label-caps text-[#747878] mb-2">Projects</div>
                  <div className="text-data-lg text-[#111111]">{projects.length}</div>
                </div>
                <div className="p-6">
                  <div className="text-label-caps text-[#747878] mb-2">Allocated</div>
                  <div className="text-data-lg text-[#111111]">{formatNaira(totalAllocated)}</div>
                </div>
                <div className="p-6">
                  <div className="text-label-caps text-[#747878] mb-2">Spent</div>
                  <div className="text-data-lg text-[#111111]">{formatNaira(totalSpent)}</div>
                </div>
                <div className="p-6">
                  <div className="text-label-caps text-[#747878] mb-2">Over-Utilized</div>
                  <div className="text-data-lg text-[#8C2929]">{overCount}</div>
                </div>
              </div>
            </div>
          </section>

          {/* Project Ledger */}
          <section className="max-w-[1200px] mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-masthead text-xl text-[#111111]">Project Ledger</h2>
              <div className="flex gap-0 divide-x divide-[#111111]">
                <button className="px-4 py-2 text-nav-label text-[#111111] hover:bg-[#E5E0D8] transition-colors">
                  EXPORT CSV
                </button>
                <button className="px-4 py-2 text-nav-label text-[#111111] hover:bg-[#E5E0D8] transition-colors">
                  EXPORT JSON
                </button>
              </div>
            </div>

            {projects.length === 0 ? (
              <div className="text-center py-12 border border-[#111111] bg-[#FCFAF5]">
                <div className="text-data-sm text-[#747878]">No projects found for this MDA</div>
              </div>
            ) : (
              <div className="border border-[#111111] bg-[#FCFAF5] overflow-x-auto">
                <table className="w-full text-left text-data-sm zebra-stripe">
                  <thead>
                    <tr className="border-b-[3px] border-[#111111] bg-[#F4F1EA]">
                      <th className="py-3 px-4 text-label-caps text-[#111111] font-normal">Project</th>
                      <th className="py-3 px-4 text-label-caps text-[#111111] font-normal">State</th>
                      <th className="py-3 px-4 text-label-caps text-[#111111] font-normal text-right">Allocated</th>
                      <th className="py-3 px-4 text-label-caps text-[#111111] font-normal text-right">Spent</th>
                      <th className="py-3 px-4 text-label-caps text-[#111111] font-normal text-right">Variance</th>
                      <th className="py-3 px-4 text-label-caps text-[#111111] font-normal text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {projects.map((p) => {
                      const v = p.budget_allocated > 0
                        ? ((p.spent - p.budget_allocated) / p.budget_allocated * 100).toFixed(1)
                        : '0.0';
                      const isOver = parseFloat(v) > 0;
                      
                      return (
                        <tr key={p.id} className="border-b border-[#E5E0D8] hover:bg-[#E5E0D8]">
                          <td className="py-3 px-4 text-[#111111]">{p.title || `Project ${p.id}`}</td>
                          <td className="py-3 px-4 text-[#747878]">{p.state || 'N/A'}</td>
                          <td className="py-3 px-4 text-right font-mono">{formatNaira(p.budget_allocated || 0)}</td>
                          <td className="py-3 px-4 text-right font-mono">{formatNaira(p.spent || 0)}</td>
                          <td className={`py-3 px-4 text-right font-mono ${isOver ? 'text-[#8C2929]' : 'text-[#2D5D40]'}`}>
                            {isOver ? '+' : ''}{v}%
                          </td>
                          <td className={`py-3 px-4 text-center font-mono ${isOver ? 'text-[#8C2929]' : 'text-[#2D5D40]'}`}>
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
