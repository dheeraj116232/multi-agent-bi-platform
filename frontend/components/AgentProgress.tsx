"use client";
import { AGENT_STEPS } from "@/types";

interface Props {
  currentAgent: string | null;
  progress: number;
  status: string | null;
  filename: string;
}

export default function AgentProgress({ currentAgent, progress, status, filename }: Props) {
  const isDone   = status === "done";
  const isFailed = status === "failed";

  return (
    <div className="card animate-fade-up" style={{ padding: "32px", overflow: "hidden", position: "relative" }}>
      {/* Scanline effect while running */}
      {status === "running" && (
        <div style={{
          position: "absolute", left: 0, right: 0, height: 1,
          background: "linear-gradient(90deg, transparent, rgba(59,130,246,0.4), transparent)",
          animation: "scanline 3s linear infinite",
          pointerEvents: "none",
        }} />
      )}

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 28 }}>
        <div>
          <p className="mono" style={{ marginBottom: 4 }}>Pipeline Status</p>
          <p style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-primary)" }}>
            {filename}
          </p>
        </div>
        <div style={{
          padding: "6px 16px", borderRadius: 999,
          background: isDone ? "rgba(16,185,129,0.1)" : isFailed ? "rgba(239,68,68,0.1)" : "rgba(59,130,246,0.1)",
          border: `1px solid ${isDone ? "rgba(16,185,129,0.3)" : isFailed ? "rgba(239,68,68,0.3)" : "rgba(59,130,246,0.3)"}`,
          color: isDone ? "#6ee7b7" : isFailed ? "#fca5a5" : "#93c5fd",
          fontSize: "0.75rem", fontWeight: 700,
          fontFamily: "var(--font-mono)", letterSpacing: "0.08em",
        }}>
          {isDone ? "✓ COMPLETE" : isFailed ? "✗ FAILED" : `${progress}%`}
        </div>
      </div>

      {/* Progress bar */}
      <div className="progress-track" style={{ marginBottom: 32 }}>
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>

      {/* Agent steps */}
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {AGENT_STEPS.map((step, i) => {
          const isActive    = currentAgent === step.name;
          const isCompleted = progress >= step.pct || isDone;
          const isPending   = !isCompleted && !isActive;

          return (
            <div key={step.name} style={{
              display: "flex", alignItems: "center", gap: 14,
              padding: "12px 16px", borderRadius: 12,
              background: isActive ? "rgba(59,130,246,0.08)" : isCompleted ? "rgba(16,185,129,0.05)" : "transparent",
              border: `1px solid ${isActive ? "rgba(59,130,246,0.25)" : isCompleted ? "rgba(16,185,129,0.15)" : "rgba(255,255,255,0.04)"}`,
              transition: "all 0.4s",
            }}>
              {/* Step indicator */}
              <div style={{
                width: 32, height: 32, borderRadius: "50%",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: isCompleted ? 14 : 16,
                background: isActive ? "rgba(59,130,246,0.2)" : isCompleted ? "rgba(16,185,129,0.15)" : "rgba(255,255,255,0.04)",
                border: `1px solid ${isActive ? "rgba(59,130,246,0.5)" : isCompleted ? "rgba(16,185,129,0.3)" : "rgba(255,255,255,0.08)"}`,
                boxShadow: isActive ? "0 0 12px rgba(59,130,246,0.4)" : "none",
                flexShrink: 0,
                transition: "all 0.4s",
              }}>
                {isCompleted ? "✓" : step.icon}
              </div>

              {/* Label */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{
                  fontSize: "0.85rem", fontWeight: 600,
                  color: isActive ? "var(--text-primary)" : isCompleted ? "#6ee7b7" : "var(--text-muted)",
                  transition: "color 0.3s",
                }}>
                  {step.label}
                </p>
                {isActive && (
                  <p className="mono" style={{ fontSize: "0.65rem", color: "var(--accent-blue)", marginTop: 2 }}>
                    processing...
                  </p>
                )}
              </div>

              {/* Right marker */}
              <div style={{
                width: 6, height: 6, borderRadius: "50%",
                background: isActive ? "var(--accent-blue)" : isCompleted ? "var(--accent-green)" : "var(--text-muted)",
                boxShadow: isActive ? "0 0 8px var(--accent-blue)" : "none",
                flexShrink: 0, transition: "all 0.4s",
              }} />
            </div>
          );
        })}
      </div>

      {isDone && (
        <div className="animate-fade-up" style={{
          marginTop: 20, padding: "14px 16px",
          background: "rgba(16,185,129,0.08)",
          border: "1px solid rgba(16,185,129,0.2)",
          borderRadius: 12, textAlign: "center",
        }}>
          <p style={{ color: "#6ee7b7", fontWeight: 600, fontSize: "0.875rem" }}>
            ✓ Analysis complete — scroll down to explore results
          </p>
        </div>
      )}
    </div>
  );
}
