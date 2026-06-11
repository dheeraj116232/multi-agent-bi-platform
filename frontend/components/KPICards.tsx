"use client";
import { JobResult } from "@/types";
import { fmt$, fmtPct } from "@/lib/api";

interface Props { result: JobResult; }

interface KPI {
  label: string;
  value: string;
  sub?: string;
  color: string;
  glow: string;
  icon: string;
  trend?: "up" | "down" | "neutral";
}

export default function KPICards({ result }: Props) {
  const { analytics, forecast, cleaning_report } = result;
  const rev  = analytics.revenue;
  const prod = analytics.product;
  const reg  = analytics.region;
  const ts   = analytics.time_series;
  const fc   = forecast;

  const mom = ts?.latest_mom_growth ?? 0;
  const momUp = mom >= 0;

  const kpis: KPI[] = [
    {
      label: "Total Revenue",
      value: fmt$(rev?.total),
      sub: `${rev?.count ?? 0} transactions`,
      color: "#3b82f6", glow: "rgba(59,130,246,0.2)", icon: "💰",
      trend: "neutral",
    },
    {
      label: "Avg Transaction",
      value: fmt$(rev?.average),
      sub: `Median ${fmt$(rev?.median)}`,
      color: "#06b6d4", glow: "rgba(6,182,212,0.2)", icon: "📊",
      trend: "neutral",
    },
    {
      label: "MoM Growth",
      value: fmtPct(mom),
      sub: `Avg ${fmtPct(ts?.avg_mom_growth)}`,
      color: momUp ? "#10b981" : "#ef4444",
      glow: momUp ? "rgba(16,185,129,0.2)" : "rgba(239,68,68,0.2)",
      icon: momUp ? "📈" : "📉",
      trend: momUp ? "up" : "down",
    },
    {
      label: "QoQ Growth",
      value: fmtPct(ts?.latest_qoq_growth),
      sub: `CAGR ${fmtPct(ts?.cagr_pct ?? null)}`,
      color: "#8b5cf6", glow: "rgba(139,92,246,0.2)", icon: "🔄",
      trend: (ts?.latest_qoq_growth ?? 0) >= 0 ? "up" : "down",
    },
    {
      label: "Top Product",
      value: prod?.top_product ?? "N/A",
      sub: `${fmt$(prod?.top_revenue)} · ${prod?.top_10?.[0]?.revenue_share_pct ?? 0}% share`,
      color: "#f59e0b", glow: "rgba(245,158,11,0.2)", icon: "🏆",
      trend: "neutral",
    },
    {
      label: "Best Region",
      value: reg?.best_region ?? "N/A",
      sub: `${fmt$(reg?.best_revenue)} revenue`,
      color: "#10b981", glow: "rgba(16,185,129,0.2)", icon: "🌍",
      trend: "neutral",
    },
    {
      label: "Next Month Forecast",
      value: fmt$(fc?.next_month),
      sub: `${fc?.best_model?.toUpperCase()} · MAPE ${fc?.best_mape_pct?.toFixed(1)}%`,
      color: "#06b6d4", glow: "rgba(6,182,212,0.2)", icon: "🔮",
      trend: (fc?.expected_growth_pct ?? 0) >= 0 ? "up" : "down",
    },
    {
      label: "Data Quality",
      value: `${cleaning_report?.quality_score ?? 0}/100`,
      sub: `${cleaning_report?.final_rows ?? 0} rows analysed`,
      color: cleaning_report?.quality_score >= 80 ? "#10b981" : "#f59e0b",
      glow: cleaning_report?.quality_score >= 80 ? "rgba(16,185,129,0.2)" : "rgba(245,158,11,0.2)",
      icon: "🛡️",
      trend: "neutral",
    },
  ];

  return (
    <div className="stagger" style={{
      display: "grid",
      gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
      gap: 16,
    }}>
      {kpis.map((kpi, i) => (
        <div key={kpi.label} className="card animate-fade-up" style={{
          padding: "22px 20px",
          position: "relative", overflow: "hidden",
        }}>
          {/* Background glow */}
          <div style={{
            position: "absolute", top: -20, right: -20,
            width: 100, height: 100, borderRadius: "50%",
            background: `radial-gradient(ellipse, ${kpi.glow} 0%, transparent 70%)`,
            pointerEvents: "none",
          }} />

          {/* Icon + trend */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
            <span style={{ fontSize: 22 }}>{kpi.icon}</span>
            {kpi.trend !== "neutral" && (
              <span style={{
                fontSize: 10, fontWeight: 700, fontFamily: "var(--font-mono)",
                color: kpi.trend === "up" ? "#6ee7b7" : "#fca5a5",
                background: kpi.trend === "up" ? "rgba(16,185,129,0.1)" : "rgba(239,68,68,0.1)",
                padding: "2px 8px", borderRadius: 999,
                border: `1px solid ${kpi.trend === "up" ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)"}`,
              }}>
                {kpi.trend === "up" ? "↑ UP" : "↓ DOWN"}
              </span>
            )}
          </div>

          {/* Value */}
          <div className="animate-count-up" style={{
            fontSize: "1.6rem", fontWeight: 800,
            color: kpi.color, lineHeight: 1,
            letterSpacing: "-0.02em", marginBottom: 6,
            textShadow: `0 0 20px ${kpi.glow}`,
            wordBreak: "break-word",
          }}>
            {kpi.value}
          </div>

          {/* Label */}
          <div className="stat-label" style={{ marginBottom: 4 }}>{kpi.label}</div>

          {/* Sub */}
          {kpi.sub && (
            <div style={{
              fontSize: "0.72rem", color: "var(--text-muted)",
              fontFamily: "var(--font-mono)",
            }}>
              {kpi.sub}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}



