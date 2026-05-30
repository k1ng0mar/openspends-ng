import { useState, useEffect } from 'react';
import { fetchProjects, type Project } from '../lib/api';
import ProjectMap from '../components/map/ProjectMap';

export default function HomePage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState({
    totalBudget: 0,
    totalSpent: 0,
    projectCount: 0,
    overUtilized: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const projData = await fetchProjects();
        setProjects(projData);
        
        const totalSpent = projData.reduce((acc: number, p: Project) => acc + (p.spent || 0), 0);
        const totalBudget = projData.reduce((acc: number, p: Project) => acc + (p.budget_allocated || 0), 0);
        
        setStats({
          totalBudget,
          totalSpent,
          projectCount: projData.length,
          overUtilized: projData.filter(p => (p.spent || 0) > (p.budget_allocated || 0) * 1.1).length,
        });
      } catch (err) {
        console.error('Failed to load home data:', err);
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

  const variance = stats.totalBudget > 0 
    ? ((stats.totalSpent - stats.totalBudget) / stats.totalBudget * 100).toFixed(1)
    : '0.0';

  return (
    <div className="min-h-screen">
      {/* === MASTHEAD SECTION === */}
      <section className="border-b-[3px] border-[#111111] bg-[#111111] py-8">
        <div className="max-w-[1200px] mx-auto px-4">
          <h1 className="font-masthead text-3xl text-[#FCFAF5]">
            Nigeria Budget Transparency Dashboard
          </h1>
          <p className="text-[#BDB8AD] mt-2 max-w-2xl">
            Federal, state, and local government spending tracked by ministry, 
            project, and geolocation. Sourced from public records.
          </p>
        </div>
      </section>

      {/* === STAT GRID === */}
      <section className="border-b-[1px] border-[#111111] bg-[#F4F1EA]">
        <div className="max-w-[1200px] mx-auto px-4 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-0 divide-x divide-y md:divide-y-0 divide-[#111111]">
            {/* Total Allocated */}
            <div className="p-6 bg-[#FCFAF5]">
              <div className="text-label-caps text-[#747878] mb-2">
                Total Allocated
              </div>
              <div className="text-data-lg text-[#111111]">
                {loading ? '---' : formatNaira(stats.totalBudget)}
              </div>
              <div className="text-data-sm text-[#BDB8AD] mt-1">
                Across all projects
              </div>
            </div>

            {/* Total Spent */}
            <div className="p-6 bg-[#FCFAF5]">
              <div className="text-label-caps text-[#747878] mb-2">
                Total Spent
              </div>
              <div className="text-data-lg text-[#111111]">
                {loading ? '---' : formatNaira(stats.totalSpent)}
              </div>
              <div className="text-data-sm text-[#BDB8AD] mt-1">
                Actual expenditure
              </div>
            </div>

            {/* Variance */}
            <div className="p-6 bg-[#FCFAF5]">
              <div className="text-label-caps text-[#747878] mb-2">
                Variance
              </div>
              <div className={`text-data-lg ${
                parseFloat(variance) > 0 ? 'text-[#8C2929]' : 'text-[#2D5D40]'
              }`}>
                {loading ? '---' : `${variance}%`}
              </div>
              <div className="text-data-sm text-[#BDB8AD] mt-1">
                {parseFloat(variance) > 0 ? 'Over budget' : 'Under budget'}
              </div>
            </div>

            {/* Active Projects */}
            <div className="p-6 bg-[#FCFAF5]">
              <div className="text-label-caps text-[#747878] mb-2">
                Active Projects
              </div>
              <div className="text-data-lg text-[#111111]">
                {loading ? '---' : stats.projectCount.toLocaleString()}
              </div>
              <div className="text-data-sm text-[#8C2929] mt-1">
                {stats.overUtilized} over-utilized
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* === MAIN CONTENT: GRID LAYOUT === */}
      <section className="max-w-[1200px] mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-0 divide-y lg:divide-y-0 lg:divide-x divide-[#111111]">
          
          {/* LEFT: Recent Transactions (spans 2 cols) */}
          <div className="lg:col-span-2 p-6 bg-[#FCFAF5] border border-[#111111]">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-masthead text-xl text-[#111111]">
                Recent Projects
              </h2>
              <a
                href="/projects"
                className="text-nav-label text-[#111111] hover:bg-[#E5E0D8] px-2 py-1 transition-colors"
              >
                VIEW ALL →
              </a>
            </div>

            {loading ? (
              <div className="text-data-sm text-[#BDB8AD] py-8 text-center">
                Loading project data...
              </div>
            ) : projects.length === 0 ? (
              <div className="text-data-sm text-[#BDB8AD] py-8 text-center">
                No projects found. Backend may be unavailable.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-data-sm zebra-stripe">
                  <thead>
                    <tr className="border-b border-[#111111]">
                      <th className="py-2 pr-4 text-label-caps text-[#747878] font-normal">Project</th>
                      <th className="py-2 pr-4 text-label-caps text-[#747878] font-normal">Ministry</th>
                      <th className="py-2 pr-4 text-label-caps text-[#747878] font-normal text-right">Allocated</th>
                      <th className="py-2 pr-4 text-label-caps text-[#747878] font-normal text-right">Spent</th>
                      <th className="py-2 text-label-caps text-[#747878] font-normal text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {projects.slice(0, 8).map((p) => {
                      const statusColor = (p.spent || 0) > (p.budget_allocated || 0) * 1.1 
                        ? 'text-[#8C2929]' 
                        : 'text-[#2D5D40]';
                      const statusText = (p.spent || 0) > (p.budget_allocated || 0) * 1.1 
                        ? 'OVER' 
                        : 'OK';
                      
                      return (
                        <tr key={p.id} className="border-b border-[#E5E0D8]">
                          <td className="py-3 pr-4 text-[#111111]">{p.title || `Project ${p.id}`}</td>
                          <td className="py-3 pr-4 text-[#747878]">{p.mda_name || 'N/A'}</td>
                          <td className="py-3 pr-4 text-right font-mono">{formatNaira(p.budget_allocated || 0)}</td>
                          <td className="py-3 pr-4 text-right font-mono">{formatNaira(p.spent || 0)}</td>
                          <td className={`py-3 text-center font-mono ${statusColor}`}>
                            {statusText}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* RIGHT: Mini Map */}
          <div className="p-6 bg-[#F4F1EA] border border-[#111111]">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-masthead text-xl text-[#111111]">
                Spatial View
              </h2>
              <a
                href="/map"
                className="text-nav-label text-[#111111] hover:bg-[#E5E0D8] px-2 py-1 transition-colors"
              >
                FULL MAP →
              </a>
            </div>
            
            <div className="border border-[#111111] bg-[#FCFAF5] h-[300px] relative">
              {loading ? (
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-data-sm text-[#BDB8AD]">Loading map...</span>
                </div>
              ) : (
                <ProjectMap projects={projects} height="300px" showControls={false} />
              )}
            </div>

            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-data-sm">
                <span className="text-[#747878]">Projects mapped</span>
                <span className="font-mono text-[#111111]">{projects.filter(p => p.latitude && p.longitude).length}</span>
              </div>
              <div className="flex justify-between text-data-sm">
                <span className="text-[#747878]">Without location</span>
                <span className="font-mono text-[#111111]">{projects.filter(p => !p.latitude || !p.longitude).length}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* === DATA SOURCES === */}
      <section className="border-t-[1px] border-[#111111] bg-[#F4F1EA] py-8">
        <div className="max-w-[1200px] mx-auto px-4">
          <div className="text-label-caps text-[#747878] mb-4">Data Sources</div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-0 divide-x divide-[#111111]">
            <div className="p-4 bg-[#FCFAF5] border border-[#111111]">
              <div className="text-data-sm text-[#111111]">Budget Office</div>
              <div className="text-data-sm text-[#BDB8AD] mt-1">Federal allocations</div>
            </div>
            <div className="p-4 bg-[#FCFAF5] border border-[#111111]">
              <div className="text-data-sm text-[#111111]">Open Treasury</div>
              <div className="text-data-sm text-[#BDB8AD] mt-1">Payments &gt;₦10M</div>
            </div>
            <div className="p-4 bg-[#FCFAF5] border border-[#111111]">
              <div className="text-data-sm text-[#111111]">BudgIT Tracka</div>
              <div className="text-data-sm text-[#BDB8AD] mt-1">GPS projects</div>
            </div>
            <div className="p-4 bg-[#FCFAF5] border border-[#111111]">
              <div className="text-data-sm text-[#111111]">NOCOPO</div>
              <div className="text-data-sm text-[#BDB8AD] mt-1">Public contracts</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
