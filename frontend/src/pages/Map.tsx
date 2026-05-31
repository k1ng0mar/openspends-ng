import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { api } from '../lib/api';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;

interface ProjectPoint {
  id: number;
  name: string;
  title?: string;
  latitude: number;
  longitude: number;
  amount: number;
  budget_allocated?: number;
  spent?: number;
  state: string;
  mda_name?: string;
}

export default function MapPage() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [projects, setProjects] = useState<ProjectPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState<ProjectPoint | null>(null);

  useEffect(() => {
    if (map.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current!,
      style: 'mapbox://styles/mapbox/light-v11', // LIGHT style for Institutional look
      center: [8.6753, 9.0820],
      zoom: 5.5,
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    map.current.on('load', async () => {
      try {
        const data = await api.get('/projects');
        const projectData = data.data || [];
        setProjects(projectData);

        projectData.forEach((p: ProjectPoint) => {
          if (!p.latitude || !p.longitude) return;
          
          // Determine status color
          const isOverUtilized = (p.spent || p.amount || 0) > (p.budget_allocated || 0) * 1.1;
          const color = isOverUtilized ? '#8C2929' : '#2D5D40'; // Oxblood or Forest

          const el = document.createElement('div');
          el.style.width = '10px';
          el.style.height = '10px';
          el.style.backgroundColor = color;
          el.style.border = '1px solid #111111';
          el.style.cursor = 'pointer';
          el.className = 'hover:scale-125 transition-transform';

          el.addEventListener('click', () => setSelectedProject(p));

          new mapboxgl.Marker(el)
            .setLngLat([p.longitude, p.latitude])
            .addTo(map.current!);
        });
      } catch (err) {
        console.error('Failed to load project map data:', err);
      } finally {
        setLoading(false);
      }
    });

    return () => map.current?.remove();
  }, []);

  const formatNaira = (amount: number) => {
    if (amount >= 1e12) return `₦${(amount / 1e12).toFixed(1)}T`;
    if (amount >= 1e9) return `₦${(amount / 1e9).toFixed(1)}B`;
    if (amount >= 1e6) return `₦${(amount / 1e6).toFixed(1)}M`;
    return `₦${amount.toLocaleString()}`;
  };

  const mappedCount = projects.filter(p => p.latitude && p.longitude).length;

  return (
    <div className="h-screen flex flex-col bg-cream-page">
      {/* Top Bar */}
      <div className="border-b-[3px] border-ink-deep bg-ink-deep text-ivory-surface">
        <div className="max-w-[1200px] mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="font-masthead text-2xl">Spatial Ledger</h1>
            <p className="text-data-sm text-ink-faint mt-1">
              {loading ? 'Loading...' : `${mappedCount} projects mapped`}
            </p>
          </div>
          <div className="flex gap-0 divide-x divide-ivory-surface">
            <button className="px-4 py-2 text-nav-label text-ivory-surface hover:bg-oxblood transition-colors">
              FILTER
            </button>
            <button className="px-4 py-2 text-nav-label text-ivory-surface hover:bg-oxblood transition-colors">
              EXPORT
            </button>
          </div>
        </div>
      </div>

      {/* Main Content: Map + Sidebar */}
      <div className="flex-1 flex flex-col lg:flex-row">
        {/* Sidebar */}
        <aside className="w-full lg:w-80 border-b lg:border-b-0 lg:border-r border-ink-deep bg-ivory-surface overflow-y-auto">
          <div className="p-4 border-b border-ink-deep">
            <div className="text-label-caps text-ink-muted mb-2">Legend</div>
            <div className="flex gap-4 text-data-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-forest border border-ink-deep" />
                <span className="text-ink-deep">On track</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-oxblood border border-ink-deep" />
                <span className="text-ink-deep">Over-utilized</span>
              </div>
            </div>
          </div>

          <div className="p-4">
            <div className="text-label-caps text-ink-muted mb-3">Project List</div>
            
            {loading ? (
              <div className="text-data-sm text-ink-faint">Loading...</div>
            ) : projects.length === 0 ? (
              <div className="text-data-sm text-ink-faint">No projects with location data</div>
            ) : (
              <div className="space-y-2">
                {projects.filter(p => p.latitude && p.longitude).slice(0, 20).map((p) => {
                  const isOver = (p.spent || p.amount || 0) > (p.budget_allocated || 0) * 1.1;
                  
                  return (
                    <button
                      key={p.id}
                      onClick={() => setSelectedProject(p)}
                      className="w-full text-left p-3 border border-ink-deep hover:bg-selection transition-colors"
                    >
                      <div className="text-data-sm text-ink-deep font-medium">
                        {p.title || p.name || `Project ${p.id}`}
                      </div>
                      <div className="text-data-sm text-ink-muted mt-1">
                        {p.state}
                      </div>
                      <div className="flex justify-between mt-2 text-data-sm">
                        <span className={`font-mono ${isOver ? 'text-oxblood' : 'text-ink-deep'}`}>
                          {formatNaira(p.spent || p.amount || 0)}
                        </span>
                        <span className={`font-mono ${isOver ? 'text-oxblood' : 'text-forest'}`}>
                          {isOver ? 'OVER' : 'OK'}
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </aside>

        {/* Map Container */}
        <div className="flex-1 relative">
          {loading && (
            <div className="absolute inset-0 z-10 bg-cream-page flex items-center justify-center">
              <div className="text-center">
                <div className="text-data-lg text-ink-deep">Loading spatial data...</div>
                <div className="text-data-sm text-ink-faint mt-2">Fetching project coordinates</div>
              </div>
            </div>
          )}
          <div ref={mapContainer} className="w-full h-full" />
        </div>

        {/* Selected Project Panel */}
        {selectedProject && (
          <div className="fixed bottom-0 left-0 right-0 lg:left-80 lg:right-auto z-20 border-t-[3px] border-ink-deep bg-ink-deep text-ivory-surface p-4">
            <div className="flex justify-between items-start">
              <div>
                <div className="text-label-caps text-ink-faint mb-1">SELECTED PROJECT</div>
                <div className="font-masthead text-xl">
                  {selectedProject.title || selectedProject.name}
                </div>
                <div className="text-data-sm text-ink-faint mt-1">
                  {selectedProject.mda_name || 'Unknown MDA'} · {selectedProject.state}
                </div>
              </div>
              <button
                onClick={() => setSelectedProject(null)}
                className="text-label-caps text-ink-faint hover:text-ivory-surface px-2"
              >
                CLOSE
              </button>
            </div>
            <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-ink-muted">
              <div>
                <div className="text-label-caps text-ink-faint">Allocated</div>
                <div className="text-data-sm font-mono mt-1">
                  {formatNaira(selectedProject.budget_allocated || 0)}
                </div>
              </div>
              <div>
                <div className="text-label-caps text-ink-faint">Spent</div>
                <div className="text-data-sm font-mono mt-1">
                  {formatNaira(selectedProject.spent || selectedProject.amount || 0)}
                </div>
              </div>
              <div>
                <div className="text-label-caps text-ink-faint">Status</div>
                <div className={`text-data-sm font-mono mt-1 ${
                  (selectedProject.spent || selectedProject.amount || 0) > (selectedProject.budget_allocated || 0) * 1.1
                    ? 'text-oxblood'
                    : 'text-forest'
                }`}>
                  {(selectedProject.spent || selectedProject.amount || 0) > (selectedProject.budget_allocated || 0) * 1.1
                    ? 'OVER-UTILIZED'
                    : 'ON TRACK'}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
