"use client";
import { useRef, useState, DragEvent, ChangeEvent } from "react";

const ACCEPTED = ".csv,.tsv,.xlsx,.xls,.xlsm,.ods,.json,.jsonl,.parquet,.xml,.zip";
const ACCEPTED_LIST = ["CSV","TSV","Excel","JSON","Parquet","XML","ZIP"];

interface Props {
  onFile: (f: File) => void;
  disabled?: boolean;
}

export default function FileUpload({ onFile, disabled }: Props) {
  const inputRef   = useRef<HTMLInputElement>(null);
  const [drag, setDrag] = useState(false);
  const [hover, setHover] = useState(false);

  function handleDrop(e: DragEvent) {
    e.preventDefault(); setDrag(false);
    const f = e.dataTransfer.files?.[0];
    if (f) onFile(f);
  }
  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) onFile(f);
  }

  return (
    <div
      className={`upload-zone ${drag ? "drag-over" : ""}`}
      style={{ padding: "64px 40px", textAlign: "center" }}
      onDragOver={e => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={disabled ? undefined : handleDrop}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onClick={() => !disabled && inputRef.current?.click()}
    >
      <input
        ref={inputRef} type="file" accept={ACCEPTED}
        style={{ display: "none" }} onChange={handleChange}
      />

      {/* Animated icon */}
      <div style={{
        width: 80, height: 80, margin: "0 auto 24px",
        background: "rgba(59,130,246,0.08)",
        border: "1px solid rgba(59,130,246,0.2)",
        borderRadius: "50%",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 32,
        transition: "all 0.3s",
        transform: drag || hover ? "scale(1.1)" : "scale(1)",
        boxShadow: drag || hover ? "0 0 30px rgba(59,130,246,0.3)" : "none",
      }}>
        {drag ? "⬇️" : "📂"}
      </div>

      <p style={{
        fontSize: "1.25rem", fontWeight: 700,
        color: "var(--text-primary)", marginBottom: 8,
        letterSpacing: "-0.01em",
      }}>
        {drag ? "Drop your file here" : "Upload your data file"}
      </p>

      <p style={{
        fontSize: "0.875rem",
        color: "var(--text-secondary)", marginBottom: 28,
      }}>
        Drag & drop or <span style={{ color: "var(--accent-blue)", fontWeight: 600 }}>browse files</span>
        {" "}— AI agents will analyse it automatically
      </p>

      {/* Format badges */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, justifyContent: "center", marginBottom: 24 }}>
        {ACCEPTED_LIST.map(f => (
          <span key={f} className="badge badge-blue">{f}</span>
        ))}
      </div>

      <button className="btn-primary" disabled={!!disabled}
        onClick={e => { e.stopPropagation(); !disabled && inputRef.current?.click(); }}>
        <span>Select File</span>
        <span>→</span>
      </button>

      <p style={{ marginTop: 16, fontSize: "0.7rem", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
        MAX 50MB · PROCESSED LOCALLY ON YOUR SERVER
      </p>
    </div>
  );
}
