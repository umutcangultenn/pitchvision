"use client";

import React, { useMemo, useState } from "react";

import { mockReports } from "@/data/demo";
import { FilterBar } from "@/components/ui/FilterBar";
import { ReportCard } from "@/components/cards/ReportCard";

export default function ReportsPage() {
  const [q, setQ] = useState("");
  const reports = useMemo(() => {
    const qq = q.toLowerCase().trim();
    if (!qq) return mockReports;
    return mockReports.filter((r) => `${r.title} ${r.reportType}`.toLowerCase().includes(qq));
  }, [q]);

  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm font-medium text-emerald-200/80">Raporlar</div>
        <h1 className="mt-1 text-2xl font-semibold text-white">Otomatik rapor kütüphanesi</h1>
        <p className="mt-2 text-sm text-text-muted">Demo: raporlar mock datadan listelenir.</p>
      </div>

      <FilterBar
        left={
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="w-72 max-w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
            placeholder="Rapor adı / türü..."
          />
        }
        right={<div className="text-sm text-text-muted">Toplam: {reports.length}</div>}
      />

      {reports.length ? (
        <div className="grid gap-4 md:grid-cols-2">
          {reports.map((r) => (
            <ReportCard key={r.id} report={r as any} />
          ))}
        </div>
      ) : (
        <div className="md:col-span-2">
          <div className="text-text-muted">Rapor bulunamadı.</div>
        </div>
      )}
    </div>
  );
}

