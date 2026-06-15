"use client";
import { useRef, useState } from "react";
import { usePipeline } from "@/hooks/usePipeline";
import FileUpload from "@/components/FileUpload";
import AgentProgress from "@/components/AgentProgress";
import KPICards from "@/components/KPICards";
import ChartGrid from "@/components/ChartGrid";
import ReportPanel from "@/components/ReportPanel";
import AnalyticsTables from "@/components/AnalyticsTables";
import Footer from "@/components/Footer";
import HowItWorks from "@/components/HowItWorks";

export default function Home() {
  const { jobId, status, progress, agent, result, error, filename, run, reset } = usePipeline();
  const [showWarnings, setShowWarnings] = useState(false);
  const resultsRef = useRef<HTMLDivElement>(null);
  const isDone     = status === "done" && result?.result;
  const data       = result?.result;

  function handleFile(file: File) {
    run(file);
    setTimeout(() => window.scrollTo({ top: 300, behavior: "smooth" }), 200);
  }

  return (
    <div className="grid-bg" style={{ minHeight: "100vh" }}>

      {/* ── Top nav ─────────────────────────────────────────────────────────── */}
      <nav style={{
        position: "sticky", top: 0, zIndex: 100,
        background: "rgba(8,12,20,0.85)",
        backdropFilter: "blur(20px)",
        borderBottom: "1px solid var(--bg-border)",
        padding: "0 40px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        height: 60,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 30, height: 30, borderRadius: 8,
            background: "linear-gradient(135deg, #2563eb, #06b6d4)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 14, fontWeight: 700, color: "white",
          }}>BI</div>
          <span style={{ fontWeight: 700, fontSize: "0.95rem", letterSpacing: "-0.01em" }}>
            bi-platform
          </span>
          <span className="badge badge-blue" style={{ marginLeft: 4 }}>v1.0</span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          {status && status !== "pending" && (
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{
                width: 6, height: 6, borderRadius: "50%",
                background: isDone ? "var(--accent-green)" : status === "failed" ? "var(--accent-red)" : "var(--accent-blue)",
                boxShadow: `0 0 8px ${isDone ? "var(--accent-green)" : status === "failed" ? "var(--accent-red)" : "var(--accent-blue)"}`,
                animation: status === "running" ? "pulse-glow 1.5s ease-in-out infinite" : "none",
              }} />
              <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", fontFamily: "var(--font-mono)" }}>
                {isDone ? "ANALYSIS COMPLETE" : status === "failed" ? "FAILED" : `${progress}% · ${agent?.toUpperCase() || "STARTING"}`}
              </span>
            </div>
          )}
          {isDone && (
            <button className="btn-ghost" onClick={reset} style={{ padding: "6px 14px", fontSize: "0.75rem" }}>
              + New Analysis
            </button>
          )}
        </div>
      </nav>

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px 80px" }}>

        {/* ── Hero ────────────────────────────────────────────────────────── */}
        {!status && (
          <div style={{ textAlign: "center", padding: "80px 0 60px" }}>
            {/* Glow orb */}
            <div style={{
              position: "relative", display: "inline-block", marginBottom: 32,
            }}>
              <div style={{
                width: 120, height: 120,
                background: "radial-gradient(circle, rgba(59,130,246,0.3) 0%, rgba(6,182,212,0.1) 50%, transparent 70%)",
                borderRadius: "50%", filter: "blur(20px)",
                position: "absolute", top: "50%", left: "50%",
                transform: "translate(-50%,-50%)",
              }} />
              <div style={{
                width: 72, height: 72, borderRadius: 20,
                background: "linear-gradient(135deg, rgba(37,99,235,0.8), rgba(6,182,212,0.8))",
                border: "1px solid rgba(59,130,246,0.4)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 30, position: "relative",
                boxShadow: "0 0 40px rgba(59,130,246,0.3)",
              }}>🤖</div>
            </div>

            <div style={{ marginBottom: 12 }}>
              <span className="mono" style={{ color: "var(--accent-cyan)" }}>
                MULTI-AGENT AI ANALYTICS
              </span>
            </div>

            <h1 className="grad-text" style={{
              fontSize: "clamp(2.4rem, 6vw, 4rem)",
              fontWeight: 800, letterSpacing: "-0.03em",
              lineHeight: 1.05, marginBottom: 20,
            }}>
              Business Intelligence<br />
              <span style={{ fontStyle: "italic", fontFamily: "var(--font-serif)" }}>powered by AI agents</span>
            </h1>

            <p style={{
              fontSize: "1.05rem", color: "var(--text-secondary)",
              maxWidth: 560, margin: "0 auto 40px",
              lineHeight: 1.7,
            }}>
              Upload any data file. Five specialised AI agents will clean, analyse,
              visualise, forecast, and write an executive report — in under 20 seconds.
            </p>

            {/* Feature pills */}
            <div style={{ display: "flex", gap: 10, justifyContent: "center", flexWrap: "wrap", marginBottom: 52 }}>
              {[
                "🧹 Auto Data Cleaning",
                "📊 Deep Analytics",
                "📈 10 AI Charts",
                "🔮 ML Forecasting",
                "📄 CEO Report + PDF",
              ].map(f => (
                <span key={f} style={{
                  padding: "6px 16px", borderRadius: 999,
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid var(--bg-border)",
                  fontSize: "0.8rem", color: "var(--text-secondary)",
                }}>{f}</span>
              ))}
            </div>

            {/* Upload zone */}
            <div style={{ maxWidth: 640, margin: "0 auto" }}>
              <FileUpload onFile={handleFile} />
            </div>
            <HowItWorks />
          </div>
        )}

        {/* ── Running / progress state ──────────────────────────────────── */}
        {status && status !== "done" && status !== "failed" && (
          <div style={{ maxWidth: 600, margin: "60px auto 0" }}>
            <AgentProgress
              currentAgent={agent}
              progress={progress}
              status={status}
              filename={filename}
            />
          </div>
        )}

        {/* ── Error state ───────────────────────────────────────────────── */}
        {status === "failed" && (
          <div style={{ maxWidth: 600, margin: "60px auto 0" }}>
            <div style={{
              padding: "28px",
              background: "rgba(239,68,68,0.08)",
              border: "1px solid rgba(239,68,68,0.3)",
              borderRadius: 16, textAlign: "center",
            }}>
              <p style={{ fontSize: 32, marginBottom: 12 }}>⚠️</p>
              <p style={{ fontWeight: 700, marginBottom: 8 }}>Pipeline Failed</p>
              <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", marginBottom: 20 }}>
                {error || "Unknown error occurred"}
              </p>
              <button className="btn-ghost" onClick={reset}>Try Again</button>
            </div>
          </div>
        )}

        {/* ── Results dashboard ────────────────────────────────────────────── */}
        {isDone && data && (
          <div ref={resultsRef} style={{ paddingTop: 48 }}>

            {/* Results header */}
            <div className="animate-fade-up" style={{
              display: "flex", alignItems: "center", justifyContent: "space-between",
              marginBottom: 32, flexWrap: "wrap", gap: 12,
            }}>
              <div>
                <p className="mono" style={{ marginBottom: 6, color: "var(--accent-cyan)" }}>
                  ANALYSIS COMPLETE · {Object.values(data.processing_time || {}).reduce((a, b) => a + b, 0).toFixed(1)}s TOTAL
                </p>
                <h1 style={{ fontSize: "2rem", fontWeight: 800, letterSpacing: "-0.02em" }}>
                  {filename}
                </h1>
              </div>
              <div style={{ display: "flex", gap: 10 }}>
                <button className="btn-ghost" onClick={reset}>
                  <span>↑</span>
                  <span>New Analysis</span>
                </button>
                {data.pdf_path && jobId && (
                  <a href={`http://localhost:8000/api/download/pdf/${jobId}`} download style={{ textDecoration: "none" }}>
                    <button className="btn-primary">
                      <span>⬇</span>
                      <span>Download PDF</span>
                    </button>
                  </a>
                )}
              </div>
            </div>

            {/* Timing badges */}
            <div className="animate-fade-up" style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 32 }}>
              {Object.entries(data.processing_time || {}).map(([agent, t]) => (
                <span key={agent} className="badge badge-blue">
                  {agent} {t}s
                </span>
              ))}
              {data.warnings?.length > 0 && (
                <span className="badge badge-amber">⚠ {data.warnings.length} warnings</span>
              )}
            </div>

            {/* KPI Cards */}
            <section style={{ marginBottom: 32 }}>
              <KPICards result={data} />
            </section>

            {/* Analytics Tables */}
            <section style={{ marginBottom: 32 }}>
              <AnalyticsTables analytics={data.analytics} />
            </section>

            {/* Charts */}
            {data.chart_metadata && jobId && (
              <section style={{ marginBottom: 32 }}>
                <ChartGrid charts={data.chart_metadata} jobId={jobId} />
              </section>
            )}

            {/* Report */}
            {jobId && (
              <section style={{ marginBottom: 32 }}>
                <ReportPanel result={data} jobId={jobId} />
              </section>
            )}

            {/* Footer note */}
            <div style={{ textAlign: "center", padding: "24px 0" }}>
              <p className="mono" style={{ color: "var(--text-muted)" }}>
                GENERATED BY 5 AI AGENTS · LANGRAPH + GROQ + XGBOOST
              </p>
            </div>
          </div>
        )}
      </div>
      <Footer />
    </div>
  );
}





