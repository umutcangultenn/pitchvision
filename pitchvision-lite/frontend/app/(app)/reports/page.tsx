"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";

import { useApi } from "@/hooks/useApi";
import { apiGetReports } from "@/lib/api";
import { FilterBar } from "@/components/ui/FilterBar";
import { ReportCard } from "@/components/cards/ReportCard";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";

export default function ReportsPage() {
  const [q, setQ] = useState("");
  const [pdfError, setPdfError] = useState(false);
  const { data: allReports, loading, error, refetch } = useApi(() => apiGetReports());

  const reports = useMemo(() => {
    const qq = q.toLowerCase().trim();
    if (!qq) return allReports ?? [];
    return (allReports ?? []).filter((r) => `${r.title} ${r.reportType}`.toLowerCase().includes(qq));
  }, [q, allReports]);

  const hasReports = (allReports?.length ?? 0) > 0;

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-10 rounded-xl bg-white/5 w-64" />
        <div className="grid gap-4 md:grid-cols-2">
          {[...Array(4)].map((_, i) => <div key={i} className="h-28 rounded-2xl bg-white/5" />)}
        </div>
      </div>
    );
  }

  if (error && !allReports) {
    return (
      <ErrorState
        title="Raporlar yüklenemedi"
        description={error.message}
        icon="📡"
        action={<button onClick={refetch} className="px-4 py-2 text-sm font-semibold rounded-xl bg-emerald-600 text-white hover:bg-emerald-500 transition-all">Yeniden Dene</button>}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm font-medium text-emerald-200/80">Raporlar</div>
        <h1 className="mt-1 text-2xl font-semibold text-white">Otomatik rapor kütüphanesi</h1>
        <p className="mt-2 text-sm text-text-muted">Demo: raporlar mock datadan listelenir.</p>
      </div>

      {/* PDF export error banner — demo toggle */}
      {pdfError && (
        <ErrorState
          title="PDF export başarısız"
          description="Rapor oluşturulurken teknik bir hata oluştu. Tarayıcıyı yenileyip tekrar dene."
          icon="📑"
          action={
            <button
              onClick={() => setPdfError(false)}
              className="px-4 py-2 text-sm font-semibold rounded-xl bg-red-600/20 border border-red-600/40 text-red-400 hover:bg-red-600/30 transition-all"
            >
              Tekrar Dene
            </button>
          }
          secondaryAction={
            <button
              onClick={() => setPdfError(false)}
              className="px-4 py-2 text-sm font-semibold rounded-xl bg-white/5 border border-white/10 text-text-soft hover:text-white transition-all"
            >
              Kapat
            </button>
          }
        />
      )}

      {!hasReports ? (
        /* No reports at all */
        <EmptyState
          title="Henüz rapor oluşturulmadı"
          description="Analiz tamamlandıktan sonra maç özeti ve detaylı raporlar burada listelenir."
          icon="📄"
          action={
            <Link
              href="/matches"
              className="px-4 py-2 text-sm font-semibold rounded-xl bg-emerald-600 text-white hover:bg-emerald-500 shadow-lg shadow-emerald-900/20 transition-all"
            >
              Maçlara Git
            </Link>
          }
        />
      ) : (
        <>
          <FilterBar
            left={
              <div className="flex items-center gap-3">
                <input
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  className="w-72 max-w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
                  placeholder="Rapor adı / türü..."
                />
                {/* Demo: trigger PDF error */}
                <button
                  onClick={() => setPdfError(true)}
                  className="px-3 py-2 text-xs rounded-xl border border-white/10 bg-white/5 text-text-muted hover:text-white transition-all"
                >
                  📥 PDF Export
                </button>
              </div>
            }
            right={<div className="text-sm text-text-muted">Toplam: {reports.length}</div>}
          />

          {reports.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {reports.map((r) => (
                <ReportCard key={r.id} report={r as any} />
              ))}
            </div>
          ) : (
            /* Filter returned no results */
            <EmptyState
              title="Filtreye uygun rapor yok"
              description={`"${q}" aramasına uygun rapor bulunamadı.`}
              icon="🔍"
              action={
                <button
                  onClick={() => setQ("")}
                  className="px-4 py-2 text-sm font-semibold rounded-xl bg-white/5 border border-white/10 text-text-soft hover:text-white transition-all"
                >
                  Aramayı Temizle
                </button>
              }
            />
          )}
        </>
      )}
    </div>
  );
}
