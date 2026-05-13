"use client";

import React from "react";

import type { TacticalMetric } from "@/types/domain";

export function TacticalMetricCard({ metric }: { metric: TacticalMetric }) {
  return (
    <div className="rounded-2xl pv-card p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-white">
            {metric.metricType.replaceAll("_", " ")}
          </div>
          <div className="mt-2 text-xs text-text-muted">
            {new Date(metric.timestamp).toLocaleString("tr-TR")}
          </div>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-center">
          <div className="text-xs text-text-muted">Değer</div>
          <div className="mt-1 text-lg font-semibold text-white">
            {metric.value}
          </div>
          <div className="mt-0.5 text-xs text-text-muted">{metric.unit || ""}</div>
        </div>
      </div>
      {metric.metadataJson ? (
        <div className="mt-4 text-sm text-text-muted">
          {Object.entries(metric.metadataJson).slice(0, 2).map(([k, v]) => (
            <div key={k} className="flex items-center justify-between gap-3">
              <span className="text-xs text-text-muted">{k}</span>
              <span className="text-xs text-white/80">{String(v)}</span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

