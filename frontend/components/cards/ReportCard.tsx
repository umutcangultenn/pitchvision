"use client";

import Link from "next/link";
import React from "react";

import type { Report } from "@/types/domain";

export function ReportCard({ report }: { report: Report }) {
  return (
    <div className="rounded-2xl pv-card p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-white">{report.title}</div>
          <div className="mt-2 flex flex-wrap gap-2 text-xs text-text-muted">
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
              {report.reportType.replaceAll("_", " ")}
            </span>
            {report.matchId ? <span>Maç #{report.matchId}</span> : null}
          </div>
          {report.summary ? (
            <div className="mt-3 line-clamp-3 text-sm text-text-muted">
              {report.summary}
            </div>
          ) : null}
        </div>

        <div className="flex flex-col items-end gap-2">
          <Link
            href={`/reports/${report.id}`}
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:border-emerald-400/40"
          >
            Gör
          </Link>
        </div>
      </div>
    </div>
  );
}

