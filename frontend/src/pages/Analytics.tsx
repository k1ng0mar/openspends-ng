import { useState, useEffect } from 'react';
import { fetchProjects, type Project } from '../lib/api';

export default function AnalyticsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchProjects();
        setProjects(data);
      } catch (err) {
        console.error('Failed to load analytics data:', err);
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

  const totalBudget = projects.reduce((acc, p) => acc + (p.budget_allocated || 0), 0);
  const totalSpent = projects.reduce((acc, p) => acc + (p.spent || 0), 0);
  const overCount = projects.filter(p => (p.spent || 0) > (p.budget_allocated || 0) * 1.1).length;

  // Group by MDA
  const mdaStats = projects.reduce((acc, p) => {
    const mda = p.mda_name || 'Unknown';
    if (!acc[mda]) acc[mda] = { allocated: 0, spent: 0, count: 0 };
    acc[mda].allocated += p.budget_allocated || 0;
    acc[mda].spent += p.spent || 0;
    acc[mda].count += 1;
    return acc;
  }, {} as Record<string, { allocated: number; spent: number; count: number }>);

  const topMDAs = Object.entries(mdaStats)
    .sort((a, b) => b[1].allocated - a[1].allocated)
    .slice(0, 10);

  return (
    <div className="min-h-screen bg-cream-page">
      {/* Header */}
      <section className="border-b-[3px] border-ink-deep bg-ink-deep py-8">
        <div className="max-w-[1200px] mx-auto px-4">
          <div className="text-label-caps text-ink-faint mb-2">VARIANCE AUDIT</div>
          <h1 className="font-masthead text-3xl text-ivory-surface">Analysis Dashboard</h1>
          <p className="text-ink-faint mt-2">
            Budget vs spending variance, ministry comparisons, and fiscal breakdowns.
          </p>
        </div>
      </section>

      {loading ? (
        <div className="text-center py-16">
          <div className="text-data-lg text-ink-deep">Loading analytics...</div>
        </div>
      ) : (
        <>
          {/* Summary Stats */}
          <section className="border-b border-ink-deep bg-ivory-surface">
            <div className="max-w-[1200px] mx-auto px-4 py-8">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-0 divide-x divide-y md:divide-y-0 divide-ink-deep">
                <div className="p-6">
                  <div className="text-label-caps text-ink-muted mb-2">Total Tracked</div>
                  <div className="text-data-lg text-ink-deep">{projects.length}</div>
                  <div className="text-data-sm text-ink-faint mt-1">projects</div>
                </div>
                <div className="p-6">
                  <div className="text-label-caps text-ink-muted mb-2">Total Allocated</div>
                  <div className="text-data-lg text-ink-deep">{formatNaira(totalBudget)}</div>
                  <div className="text-data-sm text-ink-faint mt-1">across all MDAs</div>
                </div>
                <div className="p-6">
                  <div className="text-label-caps text-ink-muted mb-2">Total Spent</div>
                  <div className="text-data-lg text-ink-deep">{formatNaira(totalSpent)}</div>
                  <div className="text-data-sm text-ink-faint mt-1">actual expenditure</div>
                </div>
                <div className="p-6">
                  <div className="text-label-caps text-ink-muted mb-2">Over-Utilized</div>
                  <div className="text-data-lg text-oxblood">{overCount}</div>
                  <div className="text-data-sm text-ink-faint mt-1">projects flagged</div>
                </div>
              </div>
            </div>
          </section>

          {/* MDA Breakdown */}
          <section className="max-w-[1200px] mx-auto px-4 py-8">
            <h2 className="font-masthead text-xl text-ink-deep mb-4">Ministry Breakdown</h2>
            
            <div className="border border-ink-deep bg-ivory-surface overflow-x-auto">
              <table className="w-full text-left text-data-sm zebra-stripe">
                <thead>
                  <tr className="border-b-[3px] border-ink-deep bg-cream-page">
                    <th className="py-3 px-4 text-label-caps text-ink-deep font-normal">Ministry / Agency</th>
                    <th className="py-3 px-4 text-label-caps text-ink-deep font-normal text-right">Projects</th>
                    <th className="py-3 px-4 text-label-caps text-ink-deep font-normal text-right">Allocated</th>
                    <th className="py-3 px-4 text-label-caps text-ink-deep font-normal text-right">Spent</th>
                    <th className="py-3 px-4 text-label-caps text-ink-deep font-normal text-right">Variance</th>
                  </tr>
                </thead>
                <tbody>
                  {topMDAs.map(([mda, stats]) => {
                    const v = stats.allocated > 0 
                      ? ((stats.spent - stats.allocated) / stats.allocated * 100).toFixed(1)
                      : '0.0';
                    const isOver = parseFloat(v) > 0;
                    
                    return (
                      <tr key={mda} className="border-b border-selection hover:bg-selection">
                        <td className="py-3 px-4 text-ink-deep">{mda}</td>
                        <td className="py-3 px-4 text-right font-mono">{stats.count}</td>
                        <td className="py-3 px-4 text-right font-mono">{formatNaira(stats.allocated)}</td>
                        <td className="py-3 px-4 text-right font-mono">{formatNaira(stats.spent)}</td>
                        <td className={`py-3 px-4 text-right font-mono ${isOver ? 'text-oxblood' : 'text-forest'}`}>
                          {isOver ? '+' : ''}{v}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>

          {/* Charts Placeholder */}
          <section className="max-w-[1200px] mx-auto px-4 py-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-0 divide-y md:divide-y-0 md:divide-x divide-ink-deep">
              <div className="p-6 border border-ink-deep bg-ivory-surface">
                <div className="text-label-caps text-ink-muted mb-4">Budget vs Spending</div>
                <div className="h-48 bg-cream-page border border-selection flex items-center justify-center">
                  <span className="text-data-sm text-ink-faint">Chart visualization pending</span>
                </div>
              </div>
              <div className="p-6 border border-ink-deep bg-ivory-surface">
                <div className="text-label-caps text-ink-muted mb-4">State Distribution</div>
                <div className="h-48 bg-cream-page border border-selection flex items-center justify-center">
                  <span className="text-data-sm text-ink-faint">Chart visualization pending</span>
                </div>
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
