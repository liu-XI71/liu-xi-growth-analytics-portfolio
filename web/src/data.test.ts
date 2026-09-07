import { describe, expect, it } from 'vitest'

import {
  CopilotDataUnavailableError,
  copilotApiUrl,
  copilotSnapshotUrl,
  loadCopilot,
} from './data'
import type { CopilotData } from './types'

const payload = {
  meta: { product_name: 'contract-fixture' },
  decisions: [],
  questions: [],
  analysis_threads: [],
  weekly_reports: [],
  cases: [],
  metric_contracts: [],
  evidence: [],
} as unknown as CopilotData

function jsonResponse(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

describe('Copilot data source priority', () => {
  it('normalizes API and public base URL slashes', () => {
    expect(copilotApiUrl('http://127.0.0.1:8000///')).toBe(
      'http://127.0.0.1:8000/api/v1/analytics/bundle',
    )
    expect(copilotApiUrl('/')).toBe('/api/v1/analytics/bundle')
    expect(copilotSnapshotUrl('/liu-xi-growth-analytics-portfolio/')).toBe(
      '/liu-xi-growth-analytics-portfolio/data/growth-analytics.json',
    )
  })

  it('uses the configured local API before the published snapshot', async () => {
    const requests: string[] = []
    const loaded = await loadCopilot({
      apiBaseUrl: 'http://127.0.0.1:8000/',
      publicBaseUrl: '/portfolio/',
      fetcher: async (input) => {
        requests.push(String(input))
        return jsonResponse(payload)
      },
    })

    expect(requests).toEqual(['http://127.0.0.1:8000/api/v1/analytics/bundle'])
    expect(loaded).toEqual({ data: payload, source: 'api' })
  })

  it('falls through an unavailable or invalid API response to the snapshot', async () => {
    const requests: string[] = []
    const loaded = await loadCopilot({
      apiBaseUrl: 'http://127.0.0.1:8000',
      publicBaseUrl: '/portfolio/',
      fetcher: async (input) => {
        requests.push(String(input))
        return requests.length === 1 ? jsonResponse({ detail: 'offline' }, 503) : jsonResponse(payload)
      },
    })

    expect(requests).toEqual([
      'http://127.0.0.1:8000/api/v1/analytics/bundle',
      '/portfolio/data/growth-analytics.json',
    ])
    expect(loaded.data).toEqual(payload)
    expect(loaded.source).toBe('snapshot')
  })

  it('does not contact an API when no API base URL is configured', async () => {
    const requests: string[] = []
    const loaded = await loadCopilot({
      apiBaseUrl: '',
      publicBaseUrl: '/liu-xi-growth-analytics-portfolio/',
      fetcher: async (input) => {
        requests.push(String(input))
        return jsonResponse(payload)
      },
    })

    expect(requests).toEqual(['/liu-xi-growth-analytics-portfolio/data/growth-analytics.json'])
    expect(loaded.source).toBe('snapshot')
  })

  it('raises an explicit error instead of displaying a second hand-written fact source', async () => {
    await expect(
      loadCopilot({
        apiBaseUrl: 'http://127.0.0.1:8000',
        publicBaseUrl: '/portfolio/',
        fetcher: async () => jsonResponse({ invalid: true }),
      }),
    ).rejects.toBeInstanceOf(CopilotDataUnavailableError)
  })
})
