import { useEffect, useRef, useCallback } from 'react'
import { createMap, addProjectMarkers, flyToState } from '../../lib/mapbox'
import type { Project } from '../../lib/api'

interface ProjectMapProps {
  projects: Project[]
  height?: string
  showControls?: boolean
  selectedState?: string | null
  onProjectClick?: (project: { id: number; title: string }) => void
  onMapReady?: (map: any) => void
}

export default function ProjectMap({
  projects,
  height = '400px',
  showControls = true,
  selectedState,
  onProjectClick,
  onMapReady,
}: ProjectMapProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<any | null>(null)
  const markersRef = useRef<any[]>([])

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    const map = createMap(containerRef.current, {
      style: 'mapbox://styles/mapbox/light-v11', // LIGHT style for Institutional
    })

    map.on('load', () => {
      onMapReady?.(map)
    })

    mapRef.current = map

    return () => {
      markersRef.current.forEach(m => m.remove())
      markersRef.current = []
      map.remove()
      mapRef.current = null
    }
  }, [])

  useEffect(() => {
    const map = mapRef.current
    if (!map || !map.isStyleLoaded()) return

    markersRef.current.forEach(m => m.remove())
    markersRef.current = []

    const validProjects = projects.filter(p => p.latitude && p.longitude)
    if (validProjects.length > 0) {
      markersRef.current = addProjectMarkers(map, validProjects, onProjectClick)
    }
  }, [projects, onProjectClick])

  useEffect(() => {
    if (selectedState && mapRef.current?.isStyleLoaded()) {
      flyToState(mapRef.current, selectedState)
    }
  }, [selectedState])

  const handleZoomIn = useCallback(() => {
    mapRef.current?.zoomIn({ duration: 500 })
  }, [])

  const handleZoomOut = useCallback(() => {
    mapRef.current?.zoomOut({ duration: 500 })
  }, [])

  const handleReset = useCallback(() => {
    mapRef.current?.flyTo({
      center: [8.6753, 9.0820],
      zoom: 5.5,
      duration: 1200,
      essential: true,
    })
  }, [])

  return (
    <div className="relative w-full h-full">
      <div ref={containerRef} style={{ width: '100%', height }} />

      {showControls && (
        <div className="absolute top-4 right-4 flex flex-col gap-1">
          <button
            onClick={handleZoomIn}
            className="w-8 h-8 bg-ivory-surface border border-ink-deep text-ink-deep hover:bg-selection transition-colors flex items-center justify-center text-lg font-mono"
            title="Zoom in"
          >
            +
          </button>
          <button
            onClick={handleZoomOut}
            className="w-8 h-8 bg-ivory-surface border border-ink-deep text-ink-deep hover:bg-selection transition-colors flex items-center justify-center text-lg font-mono"
            title="Zoom out"
          >
            −
          </button>
          <button
            onClick={handleReset}
            className="w-8 h-8 bg-ivory-surface border border-ink-deep text-ink-deep hover:bg-selection transition-colors flex items-center justify-center text-xs font-mono"
            title="Reset view"
          >
            ⌂
          </button>
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-ivory-surface border border-ink-deep px-4 py-3">
        <div className="text-label-caps text-ink-muted mb-2">Status</div>
        <div className="flex gap-3 text-data-sm">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 bg-forest" />
            <span className="text-ink-deep">On track</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 bg-oxblood" />
            <span className="text-ink-deep">Over</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 bg-ink-faint" />
            <span className="text-ink-deep">Unknown</span>
          </div>
        </div>
      </div>
    </div>
  )
}
