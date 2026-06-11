import { JobStatusResponse } from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function uploadFile(file: File): Promise<{ job_id: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/api/analyze`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function pollStatus(jobId: string): Promise<JobStatusResponse> {
  const res = await fetch(`${BASE}/api/status/${jobId}`);
  if (!res.ok) throw new Error("Status check failed");
  return res.json();
}

export function getChartUrl(jobId: string, index: number): string {
  return `${BASE}/api/chart/${jobId}/${index}`;
}

export function getPdfUrl(jobId: string): string {
  return `${BASE}/api/download/pdf/${jobId}`;
}

export function fmt$(value: number | undefined | null): string {
  if (value == null) return "N/A";
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}K`;
  return `$${value.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
}

export function fmtPct(value: number | undefined | null): string {
  if (value == null) return "N/A";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

export function confidenceColor(c: string): string {
  if (c === "high")   return "#10b981";
  if (c === "medium") return "#f59e0b";
  return "#ef4444";
}