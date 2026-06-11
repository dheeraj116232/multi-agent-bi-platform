"use client";
import { useState } from "react";
import { ChartMeta } from "@/types";
import { getChartUrl } from "@/lib/api";

interface Props {
  charts: ChartMeta[];
  jobId: string;
}

export default function ChartGrid({ charts, jobId }: Props) {
  const [selected, setSelected] = useState<number | null>(null);
  const [loaded, setLoaded]     = useState<Set<number>>(new Set());

  if (!charts?.length) return null;

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
        <div>
          <p className="mono" style={{ marginBottom: 4 }}>Visualisations</p>
          <h2 style={{ fontSize: "1.4rem", fontWeight: 700, letterSpacing: "-0.02em" }}>
            {charts.length} Charts Generated
          </h2>
        </div>
        <span className="badge badge-blue">{charts.length} total</span>
      </div>

      {/* Chart grid */}
      <div className="stagger" style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))",
        gap: 16,
      }}>
        {charts.map((chart, i) => (
          <div
            key={i}
            className="card animate-fade-up"
            style={{ cursor: "pointer", overflow: "hidden" }}
            onClick={() => setSelected(selected === i ? null : i)}
          >
            {/* Chart header */}
            <div style={{
              padding: "14px 18px",
              borderBottom: "1px solid var(--bg-border)",
              display: "flex", alignItems: "center", justifyContent: "space-between",
            }}>
              <div>
                <p style={{ fontWeight: 600, fontSize: "0.85rem" }}>{chart.title}</p>
                <p style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: 2 }}>
                  {chart.description}
                </p>
              </div>
              <span style={{
                fontSize: 10, color: "var(--text-muted)", fontFamily: "var(--font-mono)",
                padding: "2px 8px", border: "1px solid var(--bg-border)", borderRadius: 6,
              }}>
                {selected === i ? "−" : "expand"}
              </span>
            </div>

            {/* Chart image */}
            <div style={{
              background: "#fff",
              maxHeight: selected === i ? 600 : 260,
              overflow: "hidden",
              transition: "max-height 0.4s cubic-bezier(0.4,0,0.2,1)",
              position: "relative",
            }}>
              {!loaded.has(i) && (
                <div className="skeleton" style={{ position: "absolute", inset: 0 }} />
              )}
              <img
                src={getChartUrl(jobId, i)}
                alt={chart.title}
                onLoad={() => setLoaded(prev => new Set([...prev, i]))}
                style={{
                  width: "100%",
                  display: "block",
                  objectFit: "contain",
                  opacity: loaded.has(i) ? 1 : 0,
                  transition: "opacity 0.3s",
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
