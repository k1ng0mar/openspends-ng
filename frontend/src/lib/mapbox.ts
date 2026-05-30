import mapboxgl from 'mapbox-gl';

export const mapbox = mapboxgl;

export function createMap(container: HTMLDivElement, options: { style: string }) {
  return new mapboxgl.Map({
    container,
    style: options.style,
    center: [8.6753, 9.0820], // Nigeria center
    zoom: 5.5,
  });
}

export function addProjectMarkers(map: mapboxgl.Map, projects: any[], onProjectClick?: (p: any) => void) {
  return projects.map(p => {
    // Determine status color (Institutional palette)
    const isOverUtilized = (p.spent || p.amount || 0) > (p.budget_allocated || 0) * 1.1;
    const markerColor = isOverUtilized ? '#8C2929' : '#2D5D40'; // Oxblood or Forest

    const el = document.createElement('div');
    el.style.width = '10px';
    el.style.height = '10px';
    el.style.backgroundColor = markerColor;
    el.style.border = '1px solid #111111'; // Sharp contrast
    el.style.cursor = 'pointer';

    const marker = new mapboxgl.Marker(el)
      .setLngLat([p.longitude, p.latitude])
      .setPopup(
        new mapboxgl.Popup({ offset: 25, className: 'institutional-popup' }).setHTML(`
          <div style="padding: 12px; font-family: 'Libre Franklin', sans-serif; color: #1C1B1B; background: #FCFAF5; border: 1px solid #111111;">
            <div style="font-size: 10px; font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase; color: #747878; margin-bottom: 4px;">
              ${p.mda_name || 'MDA'}
            </div>
            <h3 style="margin: 0; font-family: 'Playfair Display', serif; font-weight: 700; font-size: 16px; color: #111111;">
              ${p.title || p.name || 'Unnamed Project'}
            </h3>
            <p style="margin: 4px 0; font-size: 12px; color: #747878;">
              ${p.state || 'Unknown State'}
            </p>
            <div style="margin-top: 8px; font-family: 'IBM Plex Mono', monospace; font-size: 14px; color: #111111;">
              ₦${(p.spent || p.amount || 0).toLocaleString()}
            </div>
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: ${isOverUtilized ? '#8C2929' : '#2D5D40'}; margin-top: 4px;">
              ${isOverUtilized ? 'OVER-UTILIZED' : 'ON TRACK'}
            </div>
          </div>
        `)
      )
      .addTo(map);

    marker.getElement().addEventListener('click', () => onProjectClick?.(p));
    
    return marker;
  });
}

export function flyToState(map: mapboxgl.Map, state: string) {
  const stateCoords: Record<string, [number, number]> = {
    'Lagos': [3.3792, 6.5244],
    'Kano': [8.5174, 12.0022],
    'Rivers': [6.8456, 4.8156],
    'Kaduna': [7.4300, 10.5105],
    'Oyo': [3.9470, 7.4500],
    'FCT': [7.3986, 9.0765],
    'Katsina': [7.6000, 12.9833],
    'Borno': [13.1500, 11.8333],
    'Delta': [6.2000, 5.7500],
    'Akwa Ibom': [7.9000, 4.9500],
  };

  const coords = stateCoords[state] || [8.6753, 9.0820];
  map.flyTo({ center: coords, zoom: 8, essential: true, duration: 1200 });
}
