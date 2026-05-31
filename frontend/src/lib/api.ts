import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/v1'

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Type Definitions ──

export interface State {
  id: number
  name: string
  code: string
  capital: string | null
  region: string | null
}

export interface MDA {
  id: number
  name: string
  code: string | null
  level: string | null
  state_id: number | null
  lga_id: number | null
  parent_id: number | null
  ncoa_sector: string | null
}

export interface Project {
  id: number
  title: string
  mda_id: number | null
  mda_name?: string
  state_id: number
  state?: string
  lga_id: number | null
  contractor: string | null
  start_date: string | null
  end_date: string | null
  status: string
  budget_allocated: number | null
  spent: number | null
  latitude: number | null
  longitude: number | null
  source: string | null
}

export interface Budget {
  id: number
  mda_id: number
  year_id: number
  season: string
  approved: number | null
  revised: number | null
  estimated: number | null
  spent: number | null
  variance_pct: number | null
  source_url: string | null
}

export interface Spending {
  id: number
  mda_id: number
  beneficiary: string | null
  purpose: string | null
  amount: number
  date: string
  reference: string | null
  latitude: number | null
  longitude: number | null
  source: string | null
}

export interface GeoFeature {
  type: 'Feature'
  geometry: {
    type: 'Point'
    coordinates: [number, number]
  }
  properties: {
    id: number
    title: string
    status: string
    budget_allocated: number | null
    spent: number | null
    state_id: number
  }
}

export interface VarianceDataPoint {
  year: number
  mda_id: number
  mda_name: string
  budgeted: number
  spent: number
  variance_pct: number
}

export interface GeographicPoint {
  state_id: number
  state_name: string
  total_budgeted: number
  total_spent: number
  project_count: number
}

// ── API Functions ──

export async function fetchStates(): Promise<State[]> {
  const { data } = await api.get<State[]>('/states')
  return data
}

export async function fetchMDAs(params?: {
  level?: string
  state_id?: number
  ncoa_sector?: string
  page?: number
  page_size?: number
}): Promise<MDA[]> {
  const { data } = await api.get<MDA[]>('/mdas', { params })
  return data
}

export async function fetchMDA(id: number): Promise<MDA> {
  const { data } = await api.get<MDA>(`/mdas/${id}`)
  return data
}

export async function fetchProjects(params?: {
  state_id?: number
  lga_id?: number
  status?: string
  mda_id?: number
  year?: number
  format?: 'json' | 'geojson'
  page?: number
  page_size?: number
}): Promise<Project[]> {
  const { data } = await api.get<Project[]>('/projects', { params })
  return data
}

export async function fetchProjectsGeoJSON(params?: {
  state_id?: number
  status?: string
  mda_id?: number
  year?: number
}): Promise<{ type: 'FeatureCollection'; features: GeoFeature[] }> {
  const { data } = await api.get('/projects', {
    params: { ...params, format: 'geojson' },
  })
  return data
}

export async function fetchProject(id: number): Promise<Project> {
  const { data } = await api.get<Project>(`/projects/${id}`)
  return data
}

export async function fetchBudgets(params?: {
  mda_id?: number
  state_id?: number
  year?: number
}): Promise<Budget[]> {
  const { data } = await api.get<Budget[]>('/budgets', { params })
  return data
}

export async function fetchSpending(params?: {
  mda_id?: number
  state_id?: number
  amount_min?: number
  date_from?: string
  date_to?: string
  page?: number
  page_size?: number
}): Promise<Spending[]> {
  const { data } = await api.get<Spending[]>('/spending', { params })
  return data
}

export async function fetchBudgetSpendingVariance(params?: {
  mda_id?: number
  year?: number
  state_id?: number
}): Promise<{ data: VarianceDataPoint[] }> {
  const { data } = await api.get('/analytics/budget-spending-variance', { params })
  return data
}

export async function fetchGeographicData(params?: {
  year?: number
  type?: 'spent' | 'budgeted' | 'project_count'
  level?: 'state' | 'lga'
}): Promise<{ type: 'FeatureCollection'; features: [] }> {
  const { data } = await api.get('/analytics/geographic', { params })
  return data
}

// ── Helpers ──

export function formatNaira(amount: number | null | undefined): string {
  if (amount == null) return '—'
  if (amount >= 1_000_000_000_000) return `₦${(amount / 1_000_000_000_000).toFixed(2)}T`
  if (amount >= 1_000_000_000) return `₦${(amount / 1_000_000_000).toFixed(1)}B`
  if (amount >= 1_000_000) return `₦${(amount / 1_000_000).toFixed(1)}M`
  return `₦${amount.toLocaleString()}`
}

export function formatCompact(amount: number | null | undefined): string {
  if (amount == null) return '—'
  if (amount >= 1_000_000_000_000) return `${(amount / 1_000_000_000_000).toFixed(1)}T`
  if (amount >= 1_000_000_000) return `${(amount / 1_000_000_000).toFixed(0)}B`
  if (amount >= 1_000_000) return `${(amount / 1_000_000).toFixed(0)}M`
  return amount.toLocaleString()
}

export function statusColor(status: string): string {
  switch (status) {
    case 'completed': return '#2D5D40'
    case 'in_progress': return '#111111'
    case 'abandoned': return '#8C2929'
    case 'not_started': return '#747878'
    default: return '#747878'
  }
}

export function statusLabel(status: string): string {
  switch (status) {
    case 'completed': return 'Completed'
    case 'in_progress': return 'In Progress'
    case 'abandoned': return 'Abandoned'
    case 'not_started': return 'Not Started'
    default: return status
  }
}
