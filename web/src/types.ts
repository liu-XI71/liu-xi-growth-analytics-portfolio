export type CaseId = 'referral' | 'retention' | string

export type SourceType = 'system' | 'ai' | 'human' | '系统计算' | '智能解释' | '人工确认' | string

export interface CopilotMeta {
  product_name: string
  version: string
  generated_at: string
  active_mode: string
  available_modes: string[]
  narrative_mode: string
  data_boundary: string
}

export interface DecisionItem {
  id: string
  case_id: CaseId
  title: string
  status: string
  summary: string
  recommendation: string
  gate_status: string | Record<string, boolean | null>
  evidence_ids: string[]
  claim_ids: string[]
  analysis_id: string
  anomaly?: string
  business_impact?: string
  negative_evidence?: string
  evidence_level?: string
  residual?: string
  action?: string
}

export interface AnalysisQuestion {
  id: string
  case_id: CaseId
  question: string
  answer_summary: string
  analysis_id: string
  tags: string[]
  evidence_ids: string[]
  status: string
}

export interface AnalysisStep {
  id: string
  order: number
  type: string
  title: string
  summary: string
  status: string
  evidence_ids: string[]
  chart?: { type: string; data_key: string } | null
}

export interface AnalysisThread {
  id: string
  case_id: CaseId
  title: string
  root_question: string
  status: string
  steps: AnalysisStep[]
  branches: unknown[] | Record<string, unknown>
}

export interface ReportKpi {
  metric_id?: string
  display?: string
  name?: string
  label?: string
  metric?: string
  value?: string | number | null
  change?: string | number | null
  status?: string
  source_type?: SourceType
  note?: string
}

export interface ReportEntry {
  title?: string
  text?: string
  statement?: string
  source_type?: SourceType
  evidence_ids?: string[]
}

export interface WeeklyReport {
  id: string
  case_id: CaseId
  period: string
  title: string
  headline: string
  kpis: Array<ReportKpi | string>
  anomalies: Array<ReportEntry | string>
  negative_evidence: Array<ReportEntry | string>
  hypotheses: Array<ReportEntry | string>
  experiment_status: Array<ReportEntry | string> | ReportEntry | string
  recommendations: Array<ReportEntry | string>
  limitations: Array<ReportEntry | string>
  evidence_ids: string[]
  narrative: { mode: string; status: string; text: string }
  report_mode?: string
  previous_period?: string
  data_boundary?: string
  comparison?: {
    basis: string
    metric_id: string
    previous_value: number
    current_value: number
    absolute_change_pp: number
    history_type: string
  }
  previous_snapshot?: {
    period: string
    title: string
    headline: string
    kpis: Array<ReportKpi | string>
    anomalies: Array<ReportEntry | string>
    negative_evidence: Array<ReportEntry | string>
    hypotheses: Array<ReportEntry | string>
    experiment_status: Array<ReportEntry | string> | ReportEntry | string
    recommendations: Array<ReportEntry | string>
    limitations: Array<ReportEntry | string>
    evidence_ids: string[]
    narrative: { mode: string; status: string; text: string }
  }
}

export interface GrowthCase {
  id: CaseId
  name: string
  business_question: string
  primary_metric: string
  mechanism_metric: string
  decision_metric: string
  data_boundary: string
  analysis_ids: string[]
  question_ids: string[]
  weekly_report_id: string
  analysis_data?: Record<string, unknown>
}

export interface ExperimentDefault {
  baseline?: number | null
  baseline_rate?: number | null
  mde?: number | null
  mde_absolute?: number | null
  alpha?: number | null
  power?: number | null
  daily_traffic?: number | null
  duration_days?: number | null
  total_sample?: number | null
  control_rate?: number | null
  treatment_rate?: number | null
  control_n?: number | null
  treatment_n?: number | null
  value_cost_multiple?: number | null
  external_benchmark?: number | null
  readout?: Record<string, unknown>
  [key: string]: unknown
}

export interface MetricContract {
  metric_id: string
  name: string
  role: string
  numerator: string | null
  denominator: string | null
  window: string
  grain: string
  decision_use: string
  allowed_claims: string[] | string
  forbidden_claims: string[] | string
  source_type: SourceType
}

export interface EvidenceItem {
  id: string
  case_id: CaseId
  evidence_type: string
  source_type: SourceType
  title: string
  metric_id: string | null
  values: Record<string, unknown>
  unit: string
  statement: string
  calculation: string
  claim_boundary: string
  synthetic: boolean
  source_ref: string
}

export interface CopilotData {
  meta: CopilotMeta
  decisions: DecisionItem[]
  questions: AnalysisQuestion[]
  analysis_threads: AnalysisThread[]
  weekly_reports: WeeklyReport[]
  cases: GrowthCase[]
  experiment_defaults: Record<string, ExperimentDefault>
  metric_contracts: MetricContract[]
  evidence: EvidenceItem[]
}

export interface LoadedCopilot {
  data: CopilotData
  source: 'api' | 'snapshot'
}
