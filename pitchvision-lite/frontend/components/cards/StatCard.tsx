"use client";

import React from "react";

export function StatCard({
  title,
  value,
  footer,
  tone = "accent",
}: {
  title: string;
  value: string;
  footer?: string;
  tone?: "accent" | "success" | "warning" | "danger";
}) {
  const toneClass =
    tone === "success"
      ? "border-success/30 bg-success/10"
      : tone === "warning"
      ? "border-warning/30 bg-warning/10"
      : tone === "danger"
      ? "border-danger/30 bg-danger/10"
      : "border-accent/30 bg-accent/10";

  return (
    <div className={`rounded-2xl pv-card p-5 ${toneClass}`}>
      <div className="text-sm font-medium text-text-muted">{title}</div>
      <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
      {footer ? <div className="mt-2 text-sm text-text-muted">{footer}</div> : null}
    </div>
  );
}

