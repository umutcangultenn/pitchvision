"use client";

export function SeverityBadge({ severity }: { severity: string }) {
  const tone =
    severity === "critical"
      ? "bg-danger/15 text-danger border-danger/30"
      : severity === "high"
      ? "bg-danger/10 text-danger border-danger/20"
      : severity === "medium"
      ? "bg-warning/15 text-warning border-warning/30"
      : "bg-success/15 text-success border-success/30";

  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${tone}`}>
      {severity}
    </span>
  );
}

