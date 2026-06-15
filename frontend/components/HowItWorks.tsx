"use client";

const STEPS = [
  {
    icon: "📤",
    title: "Upload Your Data",
    desc: "Drag & drop any CSV, Excel, JSON, or Parquet file with sales, revenue, or business data.",
  },
  {
    icon: "🤖",
    title: "5 AI Agents Run",
    desc: "Cleaning → Analytics → Visualization → Forecasting → Executive Report — fully automated.",
  },
  {
    icon: "📊",
    title: "Get Your Report",
    desc: "View KPIs, 10 charts, ML forecasts, and an AI-written CEO summary. Download as PDF.",
  },
];

export default function HowItWorks() {
  return (
    <div style={{ padding: "40px 0 24px", textAlign: "center" }}>
      <p className="mono" style={{ color: "var(--accent-cyan)", marginBottom: 8 }}>
        HOW IT WORKS
      </p>
      <h2 style={{
        fontSize: "1.6rem", fontWeight: 800,
        letterSpacing: "-0.02em", marginBottom: 28,
        maxWidth: 600, marginLeft: "auto", marginRight: "auto",
        lineHeight: 1.3,
      }}>
        From raw data to executive insight — automatically
      </h2>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
        gap: 16, maxWidth: 900, margin: "0 auto",
      }}>
        {STEPS.map((step, i) => (
          <div key={step.title} className="card" style={{
            padding: "22px 20px", textAlign: "left", position: "relative",
          }}>
            <div style={{
              position: "absolute", top: 16, right: 18,
              fontSize: "0.7rem", fontFamily: "var(--font-mono)",
              color: "var(--text-muted)",
            }}>
              {String(i + 1).padStart(2, "0")}
            </div>
            <div style={{ fontSize: 24, marginBottom: 10 }}>{step.icon}</div>
            <p style={{ fontWeight: 700, marginBottom: 6, fontSize: "0.9rem" }}>
              {step.title}
            </p>
            <p style={{ fontSize: "0.78rem", color: "var(--text-secondary)", lineHeight: 1.55 }}>
              {step.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}