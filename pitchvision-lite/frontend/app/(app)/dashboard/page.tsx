"use client";

import React, { useMemo } from "react";
import Link from "next/link";

import { useAppStore } from "@/lib/appStore";
import { useDashboard } from "@/hooks/useDashboard";

import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { StatCard } from "@/components/cards/StatCard";
import { MatchCard } from "@/components/cards/MatchCard";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function DashboardPage() {
  const { teamId } = useAppStore();
  const { data, loading, error, refetch } = useDashboard();

  const processedMatches = useMemo(() => {
    if (!data) return [];
    return data.recent_matches
      .filter((m) => m.teamId === teamId)
      .sort((a, b) => new Date(b.matchDate).getTime() - new Date(a.matchDate).getTime());
  }, [data, teamId]);

  const stats = useMemo(() => {
    if (!data) return [];
    const m = data.team_metrics;
    return [
      { title: "İşlenen Maç",               value: String(data.completed_matches), footer: `${data.total_matches} toplam`,        tone: "accent"  as const, href: "/matches" },
      { title: "Takip Edilen Oyuncu",        value: String(data.total_players),     footer: "U11-U17",                             tone: "success" as const, href: "/players" },
      { title: "Ortalama Takım Kompaktlığı", value: `${m.compactness} m`,           footer: `Geçiş hızı ${m.transitionSpeed} m/s`, tone: "warning" as const, href: "/matches" },
      { title: "Taktiksel Uyarı",            value: String(data.total_alerts),      footer: "Tüm maçlar",                          tone: "danger"  as const, href: "/matches" },
    ];
  }, [data]);

  // ── Loading ──────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="space-y-8 animate-pulse">
        <div className="h-16 rounded-2xl bg-white/5" />
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[...Array(4)].map((_, i) => <div key={i} className="h-28 rounded-2xl bg-white/5" />)}
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2 h-64 rounded-2xl bg-white/5" />
          <div className="h-64 rounded-2xl bg-white/5" />
        </div>
      </div>
    );
  }

  // ── Error ────────────────────────────────────────────────────────────────────
  if (error && !data) {
    return (
      <ErrorState
        title="Dashboard yüklenemedi"
        description={error.message}
        icon="📡"
        action={
          <button onClick={refetch} className="px-4 py-2 text-sm font-semibold rounded-xl bg-emerald-600 text-white hover:bg-emerald-500 transition-all">
            Yeniden Dene
          </button>
        }
      />
    );
  }

  const lastMatch = processedMatches[0];

  return (
    <div className="space-y-8">
      {/* Header */}
      <section className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="text-sm font-medium text-emerald-200/80">Hoş geldin</div>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-white">Anadolu Akademi • U15</h1>
          <p className="mt-2 max-w-2xl text-sm text-text-muted">
            {data ? `${data.completed_matches} maç işlendi, ${data.total_alerts} taktiksel uyarı üretildi.` : "—"}
          </p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <Link href="/matches/new" className="inline-flex items-center justify-center rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-500">
            Yeni Maç Yükle
          </Link>
          <Link href={lastMatch ? `/matches/${lastMatch.id}/report` : "/matches"} className="inline-flex items-center justify-center rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-text-muted hover:text-white hover:border-emerald-400/40">
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

      {/* Content */}
      <section className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <div className="text-sm font-semibold text-white">Son işlenen maçlar</div>

          {processedMatches.length ? (
            <div className="grid gap-4 md:grid-cols-2">
              {processedMatches.slice(0, 4).map((m) => (
                <MatchCard key={m.id} match={m} detailHref={`/matches/${m.id}/analysis`} />
              ))}
            </div>
          ) : (
            <EmptyState
              title="Henüz işlenen maç yok"
              description="Video yüklediğinizde işleme adımları ve raporlar burada görünecek."
              action={
                <Link href="/matches/new" className="inline-flex rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-500">
                  Yeni Maç Yükle
                </Link>
              }
            />
          )}

          {data && (
            <div className="rounded-2xl pv-card p-5">
              <div className="text-sm font-semibold text-white mb-3">Takım metrikleri</div>
              <div className="grid gap-4 md:grid-cols-3">
                {[
                  { label: "Takım boyu",    value: `${data.team_metrics.teamLength} m` },
                  { label: "Kompaktlık",    value: `${data.team_metrics.compactness} m` },
                  { label: "Geçiş hızı",   value: `${data.team_metrics.transitionSpeed} m/s` },
                ].map((item) => (
                  <div key={item.label} className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="text-xs text-text-muted">{item.label}</div>
                    <div className="mt-2 text-2xl font-semibold text-white">{item.value}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-4 lg:col-span-1">
          <div className="rounded-2xl pv-card p-5">
            <div className="flex items-start justify-between gap-3 mb-4">
              <div className="text-sm font-semibold text-white">En iyi oyuncular</div>
              <StatusBadge status="completed" />
            </div>
            {data?.top_players.length ? (
              <div className="space-y-2">
                {data.top_players.map((p) => (
                  <Link key={p.id} href={`/players/${p.id}`} className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all">
                    <div>
                      <div className="text-sm font-medium text-white">{p.firstName} {p.lastName}</div>
                      <div className="text-xs text-text-muted">{p.position}</div>
                    </div>
                    <div className="text-sm font-bold text-emerald-400">+{(p.developmentVelocity ?? 0).toFixed(2)}</div>
                  </Link>
                ))}
              </div>
            ) : (
              <EmptyState title="Oyuncu yok" description="Henüz oyuncu verisi yok." icon="👥" />
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
