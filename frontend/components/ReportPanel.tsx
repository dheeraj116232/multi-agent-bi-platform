"use client";
import { useState } from "react";
import { JobResult } from "@/types";
import { fmt$, fmtPct, getPdfUrl } from "@/lib/api";

interface Props { result: JobResult; jobId: string; }

export default function ReportPanel({ result, jobId }: Props) {
  const [tab, setTab] = useState<"summary" | "forecast" | "data">("summary");
  const { analytics, forecast, cleaning_report, report_text } = result;

  function renderMarkdown(text: string) {
    return text.split("\n").map((line, i) => {
      const stripped = line.trim();
      if (!stripped) return <div key={i} style={{ height: 8 }} />;
      if (stripped.startsWith("## ")) return (
        <h3 key={i} style={{
          fontSize: "0.95rem", fontWeight: 700, color: "var(--accent-blue)",
          letterSpacing: "0.05em", textTransform: "uppercase",
          marginTop: 24, marginBottom: 10,
          fontFamily: "var(--font-mono)",
        }}>{stripped.slice(3)}</h3>
      );
      if (stripped.startsWith("* ") || stripped.startsWith("- ")) return (
        <div key={i} style={{
          display: "flex", gap: 10, alignItems: "flex-start",
          padding: "6px 0",
        }}>
          <span style={{ color: "var(--accent-cyan)", marginTop: 2, flexShrink: 0 }}>◆</span>
          <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: 1.7 }}>
            {stripped.slice(2)}
          </p>
        </div>
      );
      if (/^\d+\. /.test(stripped)) return (
        <div key={i} style={{
          display: "flex", gap: 10, alignItems: "flex-start",
          padding: "6px 0",
        }}>
          <span style={{
            width: 22, height: 22, borderRadius: "50%", flexShrink: 0,
            background: "rgba(59,130,246,0.15)", border: "1px solid rgba(59,130,246,0.3)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "0.7rem", fontWeight: 700, color: "#93c5fd",
            fontFamily: "var(--font-mono)", marginTop: 2,
          }}>{stripped[0]}</span>
          <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: 1.7 }}>
            {stripped.slice(3)}
          </p>
        </div>
      );
      return (
        <p key={i} style={{
          fontSize: "0.875rem", color: "var(--text-secondary)",
          lineHeight: 1.7, paddingBottom: 4,
        }}>{stripped}</p>
      );
    });
  }

  return (
    <div className="card" style={{ overflow: "hidden" }}>
      {/* Header */}
      <div style={{
        padding: "24px 28px",
        borderBottom: "1px solid var(--bg-border)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        flexWrap: "wrap", gap: 12,
      }}>
        <div>
          <p className="mono" style={{ marginBottom: 4 }}>AI-Generated Analysis</p>
          <h2 style={{ fontSize: "1.3rem", fontWeight: 700, letterSpacing: "-0.02em" }}>
            Executive Report
          </h2>
        </div>
        <a
          href={getPdfUrl(jobId)}
          download
          style={{ textDecoration: "none" }}
        >
          <button className="btn-primary">
            <span>⬇</span>
            <span>Download PDF</span>
          </button>
        </a>
      </div>

      {/* Tab strip */}
      <div style={{ padding: "16px 28px", borderBottom: "1px solid var(--bg-border)" }}>
        <div className="tab-strip" style={{ width: "fit-content" }}>
          {[
            { key: "summary",  label: "📋 Summary"  },
            { key: "forecast", label: "🔮 Forecast"  },
            { key: "data",     label: "🔬 Data Quality" },
          ].map(t => (
            <div
              key={t.key}
              className={`tab-item ${tab === t.key ? "active" : ""}`}
              onClick={() => setTab(t.key as any)}
            >{t.label}</div>
          ))}
        </div>
      </div>

      {/* Tab content */}
      <div style={{ padding: "24px 28px" }}>

        {/* ── Summary tab ── */}
        {tab === "summary" && (
          <div className="animate-fade-in">
            {report_text ? renderMarkdown(report_text) : (
              <p style={{ color: "var(--text-muted)" }}>No report text available.</p>
            )}
          </div>
        )}

        {/* ── Forecast tab ── */}
        {tab === "forecast" && forecast && (
          <div className="animate-fade-in">
            {/* Model comparison */}
            <p className="mono" style={{ marginBottom: 12 }}>Model Comparison</p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px,1fr))", gap: 10, marginBottom: 28 }}>
              {Object.entries(forecast.all_models || {}).map(([model, metrics]) => {
                const isBest = model === forecast.best_model;
                return (
                  <div key={model} style={{
                    padding: "14px 16px", borderRadius: 12,
                    background: isBest ? "rgba(16,185,129,0.08)" : "var(--bg-subtle)",
                    border: `1px solid ${isBest ? "rgba(16,185,129,0.3)" : "var(--bg-border)"}`,
                  }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                      <p style={{ fontSize: "0.8rem", fontWeight: 700, textTransform: "capitalize" }}>{model}</p>
                      {isBest && <span className="badge badge-green">BEST</span>}
                    </div>
                    <p style={{ fontSize: "1.1rem", fontWeight: 700, color: isBest ? "#6ee7b7" : "var(--text-primary)" }}>
                      {metrics.mape.toFixed(1)}%
                    </p>
                    <p className="mono" style={{ fontSize: "0.6rem", marginTop: 2 }}>MAPE</p>
                  </div>
                );
              })}
            </div>

            {/* 6-month table */}
            <p className="mono" style={{ marginBottom: 12 }}>6-Month Forecast</p>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    {["Month","Forecast","Optimistic","Pessimistic"].map(h => (
                      <th key={h} style={{
                        padding: "8px 12px", textAlign: "left",
                        fontSize: "0.7rem", fontFamily: "var(--font-mono)",
                        color: "var(--text-muted)", letterSpacing: "0.1em",
                        borderBottom: "1px solid var(--bg-border)",
                      }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(forecast.forecast_6m || []).map((row, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                      <td style={{ padding: "10px 12px", fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>{row.month}</td>
                      <td style={{ padding: "10px 12px", fontWeight: 700, color: "var(--accent-cyan)" }}>{fmt$(row.forecast)}</td>
                      <td style={{ padding: "10px 12px", color: "#6ee7b7", fontSize: "0.85rem" }}>{fmt$(row.forecast * 1.2)}</td>
                      <td style={{ padding: "10px 12px", color: "#fca5a5", fontSize: "0.85rem" }}>{fmt$(row.forecast * 0.8)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Scenario cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10, marginTop: 20 }}>
              {[
                { label: "Optimistic", key: "optimistic", color: "#6ee7b7", bg: "rgba(16,185,129,0.08)", icon: "🟢" },
                { label: "Realistic",  key: "realistic",  color: "#93c5fd", bg: "rgba(59,130,246,0.08)",  icon: "🟡" },
                { label: "Pessimistic",key: "pessimistic", color: "#fca5a5", bg: "rgba(239,68,68,0.08)",  icon: "🔴" },
              ].map(s => (
                <div key={s.key} style={{
                  padding: "16px", borderRadius: 12,
                  background: s.bg, border: "1px solid rgba(255,255,255,0.06)",
                  textAlign: "center",
                }}>
                  <p style={{ fontSize: 20, marginBottom: 8 }}>{s.icon}</p>
                  <p style={{ fontSize: "1.1rem", fontWeight: 800, color: s.color }}>
                    {fmt$((forecast.scenarios as any)?.[s.key])}
                  </p>
                  <p className="mono" style={{ fontSize: "0.65rem", marginTop: 4 }}>{s.label}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Data Quality tab ── */}
        {tab === "data" && cleaning_report && (
          <div className="animate-fade-in">
            {/* Quality score */}
            <div style={{
              display: "flex", alignItems: "center", gap: 20,
              padding: "20px 24px", borderRadius: 14,
              background: cleaning_report.quality_score >= 80 ? "rgba(16,185,129,0.08)" : "rgba(245,158,11,0.08)",
              border: `1px solid ${cleaning_report.quality_score >= 80 ? "rgba(16,185,129,0.2)" : "rgba(245,158,11,0.2)"}`,
              marginBottom: 24,
            }}>
              <div style={{
                fontSize: "2.8rem", fontWeight: 800,
                color: cleaning_report.quality_score >= 80 ? "#6ee7b7" : "#fcd34d",
              }}>
                {cleaning_report.quality_score}
              </div>
              <div>
                <p style={{ fontWeight: 700, marginBottom: 2 }}>Data Quality Score</p>
                <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                  {cleaning_report.quality_score >= 90 ? "Excellent — data is clean and reliable" :
                   cleaning_report.quality_score >= 70 ? "Good — minor issues detected and fixed" :
                   "Fair — significant cleaning was performed"}
                </p>
              </div>
            </div>

            {/* Stats grid */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px,1fr))", gap: 10 }}>
              {[
                { label: "Original Rows",        value: cleaning_report.original_rows,             icon: "📥" },
                { label: "Final Rows",            value: cleaning_report.final_rows,                icon: "✅" },
                { label: "Duplicates Removed",    value: cleaning_report.exact_duplicates_removed,  icon: "🗑️" },
                { label: "Outliers Removed",      value: cleaning_report.total_outliers_removed,    icon: "🎯" },
                { label: "Currency Cols Fixed",   value: cleaning_report.currency_cols_converted?.length ?? 0, icon: "💱" },
                { label: "Date Cols Parsed",      value: cleaning_report.date_cols_parsed?.length ?? 0,        icon: "📅" },
              ].map(s => (
                <div key={s.label} style={{
                  padding: "14px 16px", borderRadius: 12,
                  background: "var(--bg-subtle)", border: "1px solid var(--bg-border)",
                }}>
                  <p style={{ fontSize: 18, marginBottom: 8 }}>{s.icon}</p>
                  <p style={{ fontSize: "1.3rem", fontWeight: 700, color: "var(--text-primary)" }}>{s.value}</p>
                  <p className="mono" style={{ fontSize: "0.65rem", marginTop: 3 }}>{s.label}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}



