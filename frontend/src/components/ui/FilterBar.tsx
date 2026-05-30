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
    <div className="bg-dark-800/80 backdrop-blur border border-dark-600 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-accent/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <span className="text-xs font-mono text-gray-400 uppercase tracking-wider">Filters</span>
        </div>
        {hasActiveFilters && (
          <button
            onClick={clearAll}
            className="text-[10px] font-mono text-accent/70 hover:text-accent transition-colors uppercase tracking-wider"
          >
            Clear All
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* State Select */}
        <div>
          <label className="block text-[10px] font-mono text-gray-500 uppercase tracking-wider mb-1.5">State</label>
          <select
            value={filters.stateId ?? ''}
            onChange={handleStateChange}
            disabled={loading}
            className="w-full bg-dark-900 border border-dark-600 rounded-lg px-3 py-2.5 text-sm text-gray-200 font-mono focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-colors appearance-none cursor-pointer disabled:opacity-40"
          >
            <option value="">All States</option>
            {states.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        {/* MDA Select */}
        <div>
          <label className="block text-[10px] font-mono text-gray-500 uppercase tracking-wider mb-1.5">MDA</label>
          <select
            value={filters.mdaId ?? ''}
            onChange={handleMdaChange}
            disabled={loading}
            className="w-full bg-dark-900 border border-dark-600 rounded-lg px-3 py-2.5 text-sm text-gray-200 font-mono focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-colors appearance-none cursor-pointer disabled:opacity-40"
          >
            <option value="">All MDAs</option>
            {mdas.map(m => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
        </div>

        {/* Status Select */}
        {showStatus && (
          <div>
            <label className="block text-[10px] font-mono text-gray-500 uppercase tracking-wider mb-1.5">Status</label>
            <select
              value={filters.status}
              onChange={handleStatusChange}
              className="w-full bg-dark-900 border border-dark-600 rounded-lg px-3 py-2.5 text-sm text-gray-200 font-mono focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-colors appearance-none cursor-pointer"
            >
              {statusOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        )}

        {/* Search */}
        {showSearch && (
          <div>
            <label className="block text-[10px] font-mono text-gray-500 uppercase tracking-wider mb-1.5">Search</label>
            <div className="relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                value={filters.search}
                onChange={handleSearchChange}
                placeholder="Search projects…"
                className="w-full pl-9 pr-3 py-2.5 bg-dark-900 border border-dark-600 rounded-lg text-sm text-gray-200 placeholder-gray-600 font-mono focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-colors"
              />
            </div>
          </div>
        )}
      </div>

      {/* Active filter pills */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-dark-700">
          {filters.stateId && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-accent/10 border border-accent/20 rounded-full text-[10px] font-mono text-accent">
              State: {states.find(s => s.id === filters.stateId)?.name}
              <button onClick={() => { onChange({ ...filters, stateId: null, mdaId: null }); loadMDAsForState(null) }} className="hover:text-white transition-colors">×</button>
            </span>
          )}
          {filters.mdaId && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-gold/10 border border-gold/20 rounded-full text-[10px] font-mono text-gold">
              MDA: {mdas.find(m => m.id === filters.mdaId)?.name}
              <button onClick={() => onChange({ ...filters, mdaId: null })} className="hover:text-white transition-colors">×</button>
            </span>
          )}
          {filters.status && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-dark-700 border border-dark-600 rounded-full text-[10px] font-mono text-gray-300">
              {filters.status.replace('_', ' ')}
              <button onClick={() => onChange({ ...filters, status: '' })} className="hover:text-white transition-colors">×</button>
            </span>
          )}
          {filters.search && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-dark-700 border border-dark-600 rounded-full text-[10px] font-mono text-gray-300">
              "{filters.search}"
              <button onClick={() => onChange({ ...filters, search: '' })} className="hover:text-white transition-colors">×</button>
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
