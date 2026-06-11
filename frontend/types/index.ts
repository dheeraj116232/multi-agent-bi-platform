export type JobStatus = "pending" | "running" | "done" | "failed";

export interface AgentStep {
  name: string;
  label: string;
  icon: string;
  pct: number;
}

export const AGENT_STEPS: AgentStep[] = [
  { name: "cleaner",    label: "Data Cleaning",    icon: "🧹", pct: 20 },
  { name: "analytics",  label: "Analytics",        icon: "📊", pct: 40 },
  { name: "visualizer", label: "Visualization",    icon: "📈", pct: 60 },
  { name: "forecaster", label: "Forecasting",      icon: "🔮", pct: 80 },
  { name: "reporter",   label: "Executive Report", icon: "📄", pct: 100 },
];

export interface RevenueKPI {
  total: number;
  average: number;
  median: number;
  max: number;
  min: number;
  std_dev: number;
  count: number;
  revenue_per_unit?: number;
}

export interface ProductData {
  top_product: string;
  top_revenue: number;
  worst_product: string;
  unique_products: number;
  pareto_80_products: number;
  top_10: Array<{
    product: string;
    total_revenue: number;
    avg_revenue: number;
    transactions: number;
    revenue_share_pct: number;
  }>;
}

export interface RegionData {
  best_region: string;
  best_revenue: number;
  worst_region: string;
  worst_revenue: number;
  performance_gap_pct: number;
  breakdown: Array<{
    region: string;
    total_revenue: number;
    avg_revenue: number;
    transactions: number;
    revenue_share_pct: number;
  }>;
}

export interface TimeSeries {
  monthly: Record<string, number>;
  quarterly: Record<string, number>;
  mom_growth_pct: Record<string, number>;
  latest_mom_growth: number;
  avg_mom_growth: number;
  latest_qoq_growth: number;
  cagr_pct?: number;
  best_month: string;
  worst_month: string;
  peak_season_month: string;
  anomaly_months: Record<string, number>;
}

export interface CustomerData {
  top_customer: string;
  top_customer_revenue: number;
  total_customers: number;
  avg_revenue_per_customer: number;
  repeat_customers: number;
  one_time_customers: number;
  top_10: Array<{
    customer: string;
    total_revenue: number;
    transactions: number;
    revenue_share_pct: number;
  }>;
}

export interface ForecastData {
  status: string;
  best_model: string;
  best_mape_pct: number;
  confidence: "high" | "medium" | "low";
  next_month: number;
  next_quarter: number;
  next_6_months: number;
  expected_growth_pct: number;
  trend_direction: string;
  forecast_3m: Array<{ month: string; forecast: number }>;
  forecast_6m: Array<{ month: string; forecast: number }>;
  scenarios: { optimistic: number; realistic: number; pessimistic: number };
  all_models: Record<string, { mae: number; rmse: number; mape: number }>;
}

export interface ChartMeta {
  path: string;
  title: string;
  description: string;
}

export interface AnalyticsResult {
  summary: {
    total_revenue: number;
    top_product: string;
    best_region: string;
    worst_region: string;
    latest_mom_growth_pct: number;
    best_month: string;
    top_customer: string;
  };
  revenue: RevenueKPI;
  product: ProductData;
  region: RegionData;
  time_series: TimeSeries;
  customer: CustomerData;
}

export interface JobResult {
  cleaning_report: {
    original_rows: number;
    final_rows: number;
    quality_score: number;
    exact_duplicates_removed: number;
    total_outliers_removed: number;
    currency_cols_converted: string[];
    date_cols_parsed: string[];
    status: string;
  };
  file_meta: {
    extension: string;
    file_size_kb: number;
    rows: number;
    cols: number;
  };
  analytics: AnalyticsResult;
  forecast: ForecastData;
  chart_count: number;
  chart_paths: string[];
  chart_metadata: ChartMeta[];
  report_text: string;
  pdf_path: string;
  errors: string[];
  warnings: string[];
  processing_time: Record<string, number>;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  current_agent: string | null;
  progress_pct: number;
  filename: string;
  result?: JobResult;
  error?: string;
}