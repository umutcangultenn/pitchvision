"use client";

import React, { useMemo } from "react";
import Link from "next/link";

import { useAppStore } from "@/lib/appStore";
import {
  demoVideoSrc,
  mockAlerts,
  mockDrills,
  mockMatches,
  mockPlayers,
  mockReports,
} from "@/data/demo";
import type { AlertType, DrillRecommendation, Match, Severity } from "@/types/domain";

import { EmptyState } from "@/components/ui/EmptyState";
import { StatCard } from "@/components/cards/StatCard";
import { MatchCard } from "@/components/cards/MatchCard";
import { AlertCard } from "@/components/cards/AlertCard";
import { DrillRecommendationCard } from "@/components/cards/DrillRecommendationCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ConfidenceBadge } from "@/components/ui/ConfidenceBadge";
import { SeverityBadge } from "@/components/ui/SeverityBadge";

const severityRank: Record<Severity, number> = {
  low: 1,
  medium: 2,
  high: 3,
  critical: 4,
};

function formatNumber(n: number) {
  return new Intl.NumberFormat("tr-TR").format(n);
}

export default function DashboardPage() {
  const { teamId } = useAppStore();

  const processedMatches = useMemo(() => {
    return mockMatches
      .filter((m) => m.teamId === teamId)
      .filter((m) => m.status === "completed" || m.status === "processing")
      .sort((a, b) => new Date(b.matchDate).getTime() - new Date(a.matchDate).getTime());
  }, [teamId]);

  const lastMatch: Match | undefined = processedMatches[0];
  const lastReport = useMemo(() => {
    const rr = [...mockReports].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    return rr.find((r) => r.matchId === lastMatch?.id) ?? rr[0];
  }, [lastMatch?.id]);

  const importantAlerts = useMemo(() => {
    // En önemli: severity + confidence
    return [...mockAlerts]
      .sort((a: any, b: any) => {
        const sa = severityRank[a.severity as Severity] ?? 0;
        const sb = severityRank[b.severity as Severity] ?? 0;
        if (sb !== sa) return sb - sa;
        return (b.confidence ?? 0) - (a.confidence ?? 0);
      })
      .slice(0, 5);
  }, []);

  const drills = useMemo(() => mockDrills.slice(0, 3), []);

  // Demo metrikleri (Stitch tasarım dili ile uyumlu, backend bağlanmadan)
  const stats = useMemo(
    () => [
      {
        title: "İşlenen Maç",
        value: "24",
        footer: "+3 bu hafta",
        tone: "accent" as const,
        href: "/matches",
      },
      {
        title: "Takip Edilen Oyuncu",
        value: "186",
        footer: "U8-U17",
        tone: "success" as const,
        href: "/players",
      },
      {
        title: "Ortalama Takım Kompaktlığı",
        value: "18.4 m",
        footer: "-2.1 m",
        tone: "warning" as const,
        href: lastMatch ? `/matches/${lastMatch.id}/analysis` : "/matches",
      },
      {
        title: "Taktiksel Uyarı",
        value: "43",
        footer: "12 yüksek öncelikli",
        tone: "danger" as const,
        href: lastMatch ? `/matches/${lastMatch.id}/analysis` : "/matches",
      },
    ],
    [lastMatch],
  );

  const lastMatchAnalysisHref = lastMatch ? `/matches/${lastMatch.id}/analysis` : "/matches";

  return (
    <div className="space-y-8">
      {/* Header + CTA */}
      <section className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="text-sm font-medium text-emerald-200/80">Hoş geldin</div>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-white">
            Anadolu Akademi • U15
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-text-muted">
            Bu hafta 3 maç işlendi, 18 yeni taktiksel uyarı üretildi.
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <Link
            href="/matches/new"
            className="inline-flex items-center justify-center rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-500"
          >
            Yeni Maç Yükle
          </Link>
          <Link
            href={
              lastReport?.matchId ? `/matches/${lastReport.matchId}/report` : "/matches/new"
            }
            className="inline-flex items-center justify-center rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-text-muted hover:text-white hover:border-emerald-400/40"
          >
            Son Raporu Aç
          </Link>
        </div>
      </section>

      {/* Stats */}
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {stats.map((s) => (
          <Link key={s.title} href={s.href} className="block">
            <StatCard title={s.title} value={s.value} footer={s.footer} tone={s.tone} />
          </Link>
        ))}
      </section>

      {/* Middle section */}
      <section className="grid gap-4 lg:grid-cols-3">
        {/* Matches + chart */}
        <div className="lg:col-span-2 space-y-4">
          <div>
            <div className="text-sm font-semibold text-white">Son işlenen maçlar</div>
            <div className="mt-1 text-sm text-text-muted">
              Demo: kartlara tıklayın → video analiz.
            </div>
          </div>

          {processedMatches.length ? (
            <div className="grid gap-4 md:grid-cols-2">
              {processedMatches.slice(0, 4).map((m) => (
                <MatchCard
                  key={m.id}
                  match={m}
                  detailHref={`/matches/${m.id}/analysis`}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              title="Henüz işlenen maç yok"
              description="Video yüklediğinizde işleme adımları ve raporlar burada görünecek."
              action={
                <Link
                  href="/matches/new"
                  className="inline-flex rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-500"
                >
                  Yeni Maç Yükle
                </Link>
              }
            />
          )}

          <div className="rounded-2xl pv-card p-5">
            <div className="text-sm font-semibold text-white">Haftalık gelişim grafiği (placeholder)</div>
            <div className="mt-2 grid gap-4 md:grid-cols-3">
              <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="text-xs text-text-muted">Takım boyu</div>
                <div className="mt-2 text-2xl font-semibold text-white">—</div>
                <div className="mt-2 text-sm text-text-muted">Yakında</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="text-xs text-text-muted">Bloklar arası mesafe</div>
                <div className="mt-2 text-2xl font-semibold text-white">—</div>
                <div className="mt-2 text-sm text-text-muted">Yakında</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="text-xs text-text-muted">Geçiş hızı</div>
                <div className="mt-2 text-2xl font-semibold text-white">—</div>
                <div className="mt-2 text-sm text-text-muted">Yakında</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right panel */}
        <div className="space-y-4 lg:col-span-1">
          <div className="rounded-2xl pv-card p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-white">En önemli 5 uyarı</div>
                <div className="mt-1 text-sm text-text-muted">
                  Demo: tıklayın → ilgili maç analiz.
                </div>
              </div>
              <div className="hidden sm:block">
                <StatusBadge status="open" />
              </div>
            </div>

            <div className="mt-4 space-y-3 max-h-[520px] overflow-y-auto pr-1">
              {importantAlerts.length ? (
                importantAlerts.map((a: any) => (
                  <Link
                    key={a.id}
                    href={`/matches/${a.matchId}/analysis`}
                    className="block"
                  >
                    <AlertCard alert={a} />
                  </Link>
                ))
              ) : (
                <EmptyState
                  title="Uyarı yok"
                  description="Bu hafta henüz uyarı üretilemedi (demo)."
                />
              )}
            </div>
          </div>

          <div className="rounded-2xl pv-card p-5">
            <div className="text-sm font-semibold text-white">Antrenman önerileri</div>
            <div className="mt-2 text-sm text-text-muted">
              Demo: en son uyarılardan türetilmiş öneriler.
            </div>

            <div className="mt-4 space-y-3">
              {drills.length ? (
                drills.map((d: any) => (
                  <Link key={d.id} href="/drills" className="block">
                    <DrillRecommendationCard drill={d} />
                  </Link>
                ))
              ) : (
                <EmptyState title="Öneri yok" description="Yakında öneri algoritması bağlanacak." />
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

