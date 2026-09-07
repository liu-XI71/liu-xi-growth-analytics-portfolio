import type { CopilotData, LoadedCopilot } from './types'

const COPILOT_BUNDLE_PATH = '/api/v1/analytics/bundle'
const COPILOT_SNAPSHOT_PATH = 'data/growth-analytics.json'
const DEFAULT_REQUEST_TIMEOUT_MS = 2500

type Fetcher = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>

export interface LoadCopilotOptions {
  apiBaseUrl?: string
  publicBaseUrl?: string
  requestTimeoutMs?: number
  fetcher?: Fetcher
}

export class CopilotDataUnavailableError extends Error {
  constructor() {
    super('Copilot data is unavailable from both the API and the published snapshot.')
    this.name = 'CopilotDataUnavailableError'
  }
}

export function isCopilotData(value: unknown): value is CopilotData {
  if (!value || typeof value !== 'object') return false
  const candidate = value as Partial<CopilotData>
  return Boolean(
    candidate.meta?.product_name
      && Array.isArray(candidate.decisions)
      && Array.isArray(candidate.questions)
      && Array.isArray(candidate.analysis_threads)
      && Array.isArray(candidate.weekly_reports)
      && Array.isArray(candidate.cases)
      && Array.isArray(candidate.metric_contracts)
      && Array.isArray(candidate.evidence),
  )
}

export function copilotApiUrl(baseUrl: string): string {
  return `${baseUrl.trim().replace(/\/+$/, '')}${COPILOT_BUNDLE_PATH}`
}

export function copilotSnapshotUrl(baseUrl: string): string {
  const normalized = baseUrl.trim() || '/'
  return `${normalized.replace(/\/+$/, '')}/${COPILOT_SNAPSHOT_PATH}`
}

async function fetchCopilot(
  url: string,
  fetcher: Fetcher,
  requestTimeoutMs: number,
): Promise<CopilotData | null> {
  const controller = new AbortController()
  const timeout = globalThis.setTimeout(() => controller.abort(), requestTimeoutMs)
  try {
    const response = await fetcher(url, {
      cache: 'no-store',
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    })
    if (!response.ok) return null
    const payload: unknown = await response.json()
    return isCopilotData(payload) ? payload : null
  } catch {
    return null
  } finally {
    globalThis.clearTimeout(timeout)
  }
}

export async function loadCopilot(options: LoadCopilotOptions = {}): Promise<LoadedCopilot> {
  const rawApiBaseUrl = (options.apiBaseUrl ?? import.meta.env.VITE_API_BASE_URL ?? '').trim()
  const publicBaseUrl = options.publicBaseUrl ?? import.meta.env.BASE_URL
  const fetcher = options.fetcher ?? globalThis.fetch.bind(globalThis)
  const requestTimeoutMs = options.requestTimeoutMs ?? DEFAULT_REQUEST_TIMEOUT_MS

  const sourceUrls: Array<{ url: string; source: LoadedCopilot['source'] }> = []
  if (rawApiBaseUrl) sourceUrls.push({ url: copilotApiUrl(rawApiBaseUrl), source: 'api' })
  sourceUrls.push({ url: copilotSnapshotUrl(publicBaseUrl), source: 'snapshot' })

  for (const { url, source } of sourceUrls) {
    const data = await fetchCopilot(url, fetcher, requestTimeoutMs)
    if (data) return { data, source }
  }

  throw new CopilotDataUnavailableError()
}
