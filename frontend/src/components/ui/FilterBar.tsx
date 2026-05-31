import { useState, useEffect, useCallback } from 'react'
import { fetchStates, fetchMDAs } from '../../lib/api'
import type { State, MDA } from '../../lib/api'

export interface FilterState {
  stateId: number | null
  mdaId: number | null
  status: string
  search: string
}

interface FilterBarProps {
  filters: FilterState
  onChange: (filters: FilterState) => void
  showSearch?: boolean
  showStatus?: boolean
  statusOptions?: Array<{ value: string; label: string }>
}

export function FilterBar({
  filters,
  onChange,
  showSearch = true,
  showStatus = true,
  statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
    { value: 'abandoned', label: 'Abandoned' },
    { value: 'not_started', label: 'Not Started' },
  ],
}: FilterBarProps) {
  const [states, setStates] = useState<State[]>([])
  const [mdas, setMDAs] = useState<MDA[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const [statesData, mdasData] = await Promise.all([
          fetchStates(),
          fetchMDAs({ level: 'fed', page_size: 100 }),
        ])
        if (!cancelled) {
          setStates(statesData)
          setMDAs(mdasData)
        }
      } catch {
        if (!cancelled) setLoading(false)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

  const loadMDAsForState = useCallback(async (stateId: number | null) => {
    if (!stateId) {
      const fedMDAs = await fetchMDAs({ level: 'fed', page_size: 100 })
      setMDAs(fedMDAs)
      return
    }
    const stateMDAs = await fetchMDAs({ state_id: stateId, page_size: 100 })
    setMDAs(stateMDAs)
  }, [])

  const handleStateChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const stateId = e.target.value ? Number(e.target.value) : null
    loadMDAsForState(stateId)
    onChange({ ...filters, stateId, mdaId: null })
  }, [filters, onChange, loadMDAsForState])

  const handleMdaChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const mdaId = e.target.value ? Number(e.target.value) : null
    onChange({ ...filters, mdaId })
  }, [filters, onChange])

  const handleStatusChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange({ ...filters, status: e.target.value })
  }, [filters, onChange])

  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...filters, search: e.target.value })
  }, [filters, onChange])

  const hasActiveFilters = filters.stateId || filters.mdaId || filters.status || filters.search

  const clearAll = useCallback(() => {
    onChange({ stateId: null, mdaId: null, status: '', search: '' })
    loadMDAsForState(null)
  }, [onChange, loadMDAsForState])

  return (
    <div className="border border-[#111111] bg-[#FCFAF5]">
      <div className="flex items-center justify-between px-4 py-2 border-b border-[#E5E0D8]">
        <span className="text-label-caps text-[#747878]">FILTERS</span>
        {hasActiveFilters && (
          <button
            onClick={clearAll}
            className="text-label-caps text-[#8C2929] hover:text-[#111111] transition-colors"
          >
            CLEAR ALL
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-0 divide-y sm:divide-y-0 sm:divide-x divide-[#111111]">
        {/* State Select */}
        <div className="p-3">
          <label className="block text-label-caps text-[#747878] mb-1">State</label>
          <select
            value={filters.stateId ?? ''}
            onChange={handleStateChange}
            disabled={loading}
            className="w-full bg-[#F4F1EA] border border-[#111111] px-3 py-2 text-data-sm text-[#111111] font-mono focus:outline-none focus:border-[#111111] transition-colors appearance-none cursor-pointer disabled:opacity-40"
          >
            <option value="">All States</option>
            {states.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        {/* MDA Select */}
        <div className="p-3">
          <label className="block text-label-caps text-[#747878] mb-1">MDA</label>
          <select
            value={filters.mdaId ?? ''}
            onChange={handleMdaChange}
            disabled={loading}
            className="w-full bg-[#F4F1EA] border border-[#111111] px-3 py-2 text-data-sm text-[#111111] font-mono focus:outline-none focus:border-[#111111] transition-colors appearance-none cursor-pointer disabled:opacity-40"
          >
            <option value="">All MDAs</option>
            {mdas.map(m => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
        </div>

        {/* Status Select */}
        {showStatus && (
          <div className="p-3">
            <label className="block text-label-caps text-[#747878] mb-1">Status</label>
            <select
              value={filters.status}
              onChange={handleStatusChange}
              className="w-full bg-[#F4F1EA] border border-[#111111] px-3 py-2 text-data-sm text-[#111111] font-mono focus:outline-none focus:border-[#111111] transition-colors appearance-none cursor-pointer"
            >
              {statusOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        )}

        {/* Search */}
        {showSearch && (
          <div className="p-3">
            <label className="block text-label-caps text-[#747878] mb-1">Search</label>
            <input
              type="text"
              value={filters.search}
              onChange={handleSearchChange}
              placeholder="Search projects…"
              className="w-full bg-[#F4F1EA] border border-[#111111] px-3 py-2 text-data-sm text-[#111111] placeholder-[#BDB8AD] font-mono focus:outline-none focus:border-[#111111] transition-colors"
            />
          </div>
        )}
      </div>

      {/* Active filter pills */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2 px-4 py-2 border-t border-[#E5E0D8]">
          {filters.stateId && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 border border-[#111111] bg-[#F4F1EA] text-data-sm text-[#111111] font-mono">
              {states.find(s => s.id === filters.stateId)?.name}
              <button onClick={() => { onChange({ ...filters, stateId: null, mdaId: null }); loadMDAsForState(null) }} className="ml-0.5 text-[#8C2929] hover:text-[#111111] transition-colors">×</button>
            </span>
          )}
          {filters.mdaId && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 border border-[#111111] bg-[#F4F1EA] text-data-sm text-[#111111] font-mono">
              {mdas.find(m => m.id === filters.mdaId)?.name}
              <button onClick={() => onChange({ ...filters, mdaId: null })} className="ml-0.5 text-[#8C2929] hover:text-[#111111] transition-colors">×</button>
            </span>
          )}
          {filters.status && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 border border-[#111111] bg-[#F4F1EA] text-data-sm text-[#111111] font-mono">
              {filters.status.replace('_', ' ')}
              <button onClick={() => onChange({ ...filters, status: '' })} className="ml-0.5 text-[#8C2929] hover:text-[#111111] transition-colors">×</button>
            </span>
          )}
          {filters.search && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 border border-[#111111] bg-[#F4F1EA] text-data-sm text-[#111111] font-mono">
              "{filters.search}"
              <button onClick={() => onChange({ ...filters, search: '' })} className="ml-0.5 text-[#8C2929] hover:text-[#111111] transition-colors">×</button>
            </span>
          )}
        </div>
      )}
    </div>
  )
}

export const defaultFilters: FilterState = {
  stateId: null,
  mdaId: null,
  status: '',
  search: '',
}
