"use client";

import React from "react";

import type { TacticalAlert } from "@/types/domain";
import { ConfidenceBadge } from "@/components/ui/ConfidenceBadge";
import { SeverityBadge } from "@/components/ui/SeverityBadge";
import { StatusBadge } from "@/components/ui/StatusBadge";

export function AlertCard({ alert }: { alert: TacticalAlert }) {
  return (
    <div className="rounded-2xl pv-card p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-white">{alert.title}</div>
          {alert.description ? (
            <div className="mt-2 text-sm text-text-muted line-clamp-2">
              {alert.description}
            </div>
          ) : null}
          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge status={alert.status} />
            <SeverityBadge severity={alert.severity} />
            {typeof alert.confidence === "number" ? (
              <ConfidenceBadge value={alert.confidence} />
            ) : null}
          </div>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-center">
          <div className="text-xs text-text-muted">Aralık</div>
          <div className="mt-1 text-sm font-semibold text-white">
            {Math.round(alert.startTime)}s - {Math.round(alert.endTime)}s
          </div>
        </div>
      </div>
    </div>
  );
}

