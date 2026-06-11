"use client";
import { useState, useRef, useCallback } from "react";
import { uploadFile, pollStatus } from "@/lib/api";
import { JobStatusResponse, JobStatus } from "@/types";

export function usePipeline() {
  const [jobId,    setJobId]    = useState<string | null>(null);
  const [status,   setStatus]   = useState<JobStatus | null>(null);
  const [progress, setProgress] = useState(0);
  const [agent,    setAgent]    = useState<string | null>(null);
  const [result,   setResult]   = useState<JobStatusResponse | null>(null);
  const [error,    setError]    = useState<string | null>(null);
  const [filename, setFilename] = useState<string>("");
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const startPolling = useCallback((id: string) => {
    intervalRef.current = setInterval(async () => {
      try {
        const data = await pollStatus(id);
        setStatus(data.status);
        setProgress(data.progress_pct ?? 0);
        setAgent(data.current_agent);
        if (data.status === "done" || data.status === "failed") {
          stopPolling();
          setResult(data);
          if (data.status === "failed") setError(data.error || "Pipeline failed");
        }
      } catch (e) {
        stopPolling();
        setError("Connection error — is the backend running?");
      }
    }, 2000);
  }, [stopPolling]);

  const run = useCallback(async (file: File) => {
    setError(null);
    setResult(null);
    setStatus("pending");
    setProgress(0);
    setAgent(null);
    setFilename(file.name);
    try {
      const { job_id } = await uploadFile(file);
      setJobId(job_id);
      setStatus("running");
      startPolling(job_id);
    } catch (e: any) {
      setError(e.message || "Upload failed");
      setStatus("failed");
    }
  }, [startPolling]);

  const reset = useCallback(() => {
    stopPolling();
    setJobId(null); setStatus(null); setProgress(0);
    setAgent(null); setResult(null); setError(null); setFilename("");
  }, [stopPolling]);

  return { jobId, status, progress, agent, result, error, filename, run, reset };
}