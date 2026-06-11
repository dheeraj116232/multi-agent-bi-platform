"use client";
import { useState } from "react";
import { AnalyticsResult } from "@/types";
import { fmt$, fmtPct } from "@/lib/api";

interface Props { analytics: AnalyticsResult; }

export default function AnalyticsTables({ analytics }: Props) {
  const [tab, setTab] = useState<"products" | "regions" | "customers" | "timeseries">("products");
  const { product, region, customer, time_series } = analytics;

  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <div style={{
        padding: "20px 24px", borderBottom: "1px solid var(--bg-border)",
        display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12,
      }}>
        <div>
          <p className="mono" style={{ marginBottom: 4 }}>Deep Dive</p>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 700 }}>Analytics Breakdown</h2>
        </div>
        <div className="tab-strip">
          {([
            { key: "products",   label: "Products"   },
            { key: "regions",    label: "Regions"     },
            { key: "customers",  label: "Customers"   },
            { key: "timeseries", label: "Time Series" },
          ] as const).map(t => (
            <div key={t.key} className={`tab-item ${tab === t.key ? "active" : ""}`}
              onClick={() => setTab(t.key)}>{t.label}</div>
          ))}
        </div>
      </div>

      <div style={{ padding: "20px 24px", overflowX: "auto" }}>

        {/* ── Products ── */}
        {tab === "products" && product && (
          <div className="animate-fade-in">
            <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
              <span className="badge badge-amber">🏆 {product.top_product}</span>
              <span className="badge badge-blue">{product.unique_products} products</span>
              <span className="badge badge-purple">Top {product.pareto_80_products} = 80% revenue</span>
            </div>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {["Product","Total Revenue","Avg Revenue","Transactions","Share %","Bar"].map(h => (
                    <th key={h} style={{ padding: "8px 12px", textAlign: "left", fontSize: "0.7rem",
                      fontFamily: "var(--font-mono)", color: "var(--text-muted)", letterSpacing: "0.08em",
                      borderBottom: "1px solid var(--bg-border)", whiteSpace: "nowrap" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {product.top_10?.map((row, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                    <td style={{ padding: "10px 12px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        {i === 0 && <span style={{ fontSize: 12 }}>🏆</span>}
                        <span style={{ fontWeight: 600, fontSize: "0.85rem" }}>{row.product}</span>
                      </div>
                    </td>
                    <td style={{ padding: "10px 12px", fontWeight: 700, color: "var(--accent-cyan)" }}>{fmt$(row.total_revenue)}</td>
                    <td style={{ padding: "10px 12px", color: "var(--text-secondary)", fontSize: "0.85rem" }}>{fmt$(row.avg_revenue)}</td>
                    <td style={{ padding: "10px 12px", fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>{row.transactions}</td>
                    <td style={{ padding: "10px 12px" }}>
                      <span className="badge badge-blue">{row.revenue_share_pct}%</span>
                    </td>
                    <td style={{ padding: "10px 12px", minWidth: 100 }}>
                      <div style={{ height: 6, background: "var(--bg-border)", borderRadius: 3, overflow: "hidden" }}>
                        <div style={{
                          height: "100%", width: `${row.revenue_share_pct}%`,
                          background: "linear-gradient(90deg, var(--accent-blue), var(--accent-cyan))",
                          borderRadius: 3,
                        }} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* ── Regions ── */}
        {tab === "regions" && region && (
          <div className="animate-fade-in">
            <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
              <span className="badge badge-green">🌍 Best: {region.best_region}</span>
              <span className="badge badge-red">⚠ Worst: {region.worst_region}</span>
              <span className="badge badge-amber">Gap: {region.performance_gap_pct?.toFixed(1)}%</span>
            </div>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {["Region","Total Revenue","Avg Revenue","Transactions","Share %","Bar"].map(h => (
                    <th key={h} style={{ padding: "8px 12px", textAlign: "left", fontSize: "0.7rem",
                      fontFamily: "var(--font-mono)", color: "var(--text-muted)", letterSpacing: "0.08em",
                      borderBottom: "1px solid var(--bg-border)", whiteSpace: "nowrap" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {region.breakdown?.map((row, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                    <td style={{ padding: "10px 12px", fontWeight: 600, fontSize: "0.85rem" }}>{row.region}</td>
                    <td style={{ padding: "10px 12px", fontWeight: 700, color: "var(--accent-green)" }}>{fmt$(row.total_revenue)}</td>
                    <td style={{ padding: "10px 12px", color: "var(--text-secondary)", fontSize: "0.85rem" }}>{fmt$(row.avg_revenue)}</td>
                    <td style={{ padding: "10px 12px", fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>{row.transactions}</td>
                    <td style={{ padding: "10px 12px" }}>
                      <span className="badge badge-green">{row.revenue_share_pct}%</span>
                    </td>
                    <td style={{ padding: "10px 12px", minWidth: 100 }}>
                      <div style={{ height: 6, background: "var(--bg-border)", borderRadius: 3, overflow: "hidden" }}>
                        <div style={{
                          height: "100%", width: `${row.revenue_share_pct}%`,
                          background: "linear-gradient(90deg, var(--accent-green), #06b6d4)",
                          borderRadius: 3,
                        }} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* ── Customers ── */}
        {tab === "customers" && customer && (
          <div className="animate-fade-in">
            <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
              <span className="badge badge-amber">👑 {customer.top_customer}</span>
              <span className="badge badge-green">{customer.repeat_customers} repeat buyers</span>
              <span className="badge badge-blue">Avg {fmt$(customer.avg_revenue_per_customer)}/customer</span>
            </div>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {["Customer","Total Revenue","Transactions","Share %","Bar"].map(h => (
                    <th key={h} style={{ padding: "8px 12px", textAlign: "left", fontSize: "0.7rem",
                      fontFamily: "var(--font-mono)", color: "var(--text-muted)", letterSpacing: "0.08em",
                      borderBottom: "1px solid var(--bg-border)", whiteSpace: "nowrap" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {customer.top_10?.map((row, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                    <td style={{ padding: "10px 12px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        {i === 0 && <span style={{ fontSize: 12 }}>👑</span>}
                        <span style={{ fontWeight: 600, fontSize: "0.85rem" }}>{row.customer}</span>
                      </div>
                    </td>
                    <td style={{ padding: "10px 12px", fontWeight: 700, color: "var(--accent-amber)" }}>{fmt$(row.total_revenue)}</td>
                    <td style={{ padding: "10px 12px", fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>{row.transactions}</td>
                    <td style={{ padding: "10px 12px" }}>
                      <span className="badge badge-amber">{row.revenue_share_pct}%</span>
                    </td>
                    <td style={{ padding: "10px 12px", minWidth: 100 }}>
                      <div style={{ height: 6, background: "var(--bg-border)", borderRadius: 3, overflow: "hidden" }}>
                        <div style={{
                          height: "100%", width: `${row.revenue_share_pct}%`,
                          background: "linear-gradient(90deg, var(--accent-amber), #f97316)",
                          borderRadius: 3,
                        }} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* ── Time Series ── */}
        {tab === "timeseries" && time_series && (
          <div className="animate-fade-in">
            <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
              <span className="badge badge-green">📅 Best: {time_series.best_month}</span>
              <span className="badge badge-red">📉 Worst: {time_series.worst_month}</span>
              <span className="badge badge-amber">🌟 Peak: {time_series.peak_season_month}</span>
              {time_series.cagr_pct != null && <span className="badge badge-purple">CAGR {fmtPct(time_series.cagr_pct)}</span>}
            </div>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {["Month","Revenue","MoM Growth","Trend"].map(h => (
                    <th key={h} style={{ padding: "8px 12px", textAlign: "left", fontSize: "0.7rem",
                      fontFamily: "var(--font-mono)", color: "var(--text-muted)", letterSpacing: "0.08em",
                      borderBottom: "1px solid var(--bg-border)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(time_series.monthly || {}).sort().map(([month, rev], i) => {
                  const mom = time_series.mom_growth_pct?.[month];
                  const isAnomaly = month in (time_series.anomaly_months || {});
                  return (
                    <tr key={month} style={{
                      borderBottom: "1px solid rgba(255,255,255,0.04)",
                      background: isAnomaly ? "rgba(239,68,68,0.05)" : "transparent",
                    }}>
                      <td style={{ padding: "10px 12px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>{month}</span>
                          {isAnomaly && <span className="badge badge-red">ANOMALY</span>}
                        </div>
                      </td>
                      <td style={{ padding: "10px 12px", fontWeight: 700, color: "var(--text-primary)" }}>{fmt$(rev)}</td>
                      <td style={{ padding: "10px 12px" }}>
                        {mom != null ? (
                          <span style={{ color: mom >= 0 ? "#6ee7b7" : "#fca5a5", fontWeight: 600, fontSize: "0.85rem" }}>
                            {fmtPct(mom)}
                          </span>
                        ) : <span style={{ color: "var(--text-muted)" }}>—</span>}
                      </td>
                      <td style={{ padding: "10px 12px", minWidth: 120 }}>
                        <div style={{ height: 6, background: "var(--bg-border)", borderRadius: 3, overflow: "hidden" }}>
                          <div style={{
                            height: "100%",
                            width: `${(rev / Math.max(...Object.values(time_series.monthly))) * 100}%`,
                            background: isAnomaly
                              ? "linear-gradient(90deg,#ef4444,#f97316)"
                              : "linear-gradient(90deg,var(--accent-purple),var(--accent-blue))",
                            borderRadius: 3,
                          }} />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
