"use client";

export function ConfidenceBadge({ value }: { value: number }) {
  const v = Math.max(0, Math.min(1, value));
  const pct = Math.round(v * 100);
  const tone =
    pct >= 80 ? "bg-success/15 text-success border-success/30" : pct >= 55 ? "bg-warning/15 text-warning border-warning/30" : "bg-danger/15 text-danger border-danger/30";

  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${tone}`}>
      {pct}%
    </span>
  );
}

