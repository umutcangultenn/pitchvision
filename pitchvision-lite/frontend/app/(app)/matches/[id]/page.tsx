"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { demoVideoSrc, mockAlerts, mockMatches, mockPlayers, mockVideos } from "@/data/demo";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { TacticalMetricCard } from "@/components/cards/TacticalMetricCard";
import { VideoPlayer } from "@/components/media/VideoPlayer";
import { AlertCard } from "@/components/cards/AlertCard";
import { Timeline, type TimelineItem } from "@/components/ui/Timeline";

import type { Match, TacticalMetric } from "@/types/domain";

const subTabs = [
  { key: "processing", label: "İşleme", href: (id: string) => `/matches/${id}/processing` },
  { key: "calibration", label: "Kalibrasyon", href: (id: string) => `/matches/${id}/calibration` },
  { key: "analysis", label: "Analiz", href: (id: string) => `/matches/${id}/analysis` },
  { key: "report", label: "Rapor", href: (id: string) => `/matches/${id}/report` },
];

export default function MatchDetailPage() {
  const params = useParams();
  const idParam = String(params.id);
  const matchId = Number(idParam);

  const match = useMemo(() => {
    if (!Number.isFinite(matchId)) return mockMatches[0];
    return mockMatches.find((m) => m.id === matchId) ?? mockMatches[0];
  }, [matchId]);
  const effectiveMatchId = Number.isFinite(matchId) ? matchId : match.id;
  const video = useMemo(() => mockVideos.find((v) => v.matchId === effectiveMatchId), [effectiveMatchId]);
  const alerts = useMemo(() => mockAlerts.filter((a) => a.matchId === effectiveMatchId), [effectiveMatchId]);

  const timelineItems: TimelineItem[] = useMemo(
    () => [
      { id: "t1", title: "Yükleme tamamlandı", timeLabel: "07:30", tone: "success" },
      { id: "t2", title: "Kalibrasyon", timeLabel: "07:50", tone: "accent" },
      { id: "t3", title: "Taktik metrikler", timeLabel: "08:20", tone: "warning" },
      { id: "t4", title: "Rapor üretimi", timeLabel: "09:05", tone: "accent" },
    ],
    [],
  );

  const idStr = String(Number.isFinite(matchId) ? effectiveMatchId : idParam);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="text-sm text-emerald-200/80">Maç #{idStr}</div>
          <h1 className="mt-1 text-2xl font-semibold text-white">{match.opponentName}</h1>
          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge status={match.status} />
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-text-muted">
              {match.ageCategory} • {match.gameFormat}
            </span>
          </div>
          <div className="mt-3 text-sm text-text-muted">
            Skor: <span className="text-white font-semibold">{match.scoreFor}:{match.scoreAgainst}</span>
          </div>
        </div>

        <div className="rounded-2xl pv-card p-4 w-full md:w-80">
          <div className="text-sm font-semibold text-white">Hızlı geçiş</div>
          <div className="mt-3 flex flex-wrap gap-2">
            {subTabs.map((t) => (
              <Link
                key={t.key}
                href={t.href(idStr)}
                className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-text-muted hover:text-white hover:border-emerald-400/40"
              >
                {t.label}
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <Timeline items={timelineItems} />
          <div className="grid gap-4 sm:grid-cols-2">
            {/* Demo: alert + metric cards birlikte */}
            {alerts.slice(0, 2).map((a: any) => (
              <AlertCard key={a.id} alert={a} />
            ))}
          </div>
        </div>

        <div className="lg:col-span-1 space-y-4">
          <div className="rounded-2xl pv-card p-5">
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold text-white">Video</div>
              <div className="text-xs text-text-muted">{video?.status ?? "—"}</div>
            </div>
            <div className="mt-4">
              <VideoPlayer src={demoVideoSrc} title="Maç videosu (demo)" />
            </div>
          </div>

          <div className="rounded-2xl pv-card p-5">
            <div className="text-sm font-semibold text-white">Öne çıkan oyuncular</div>
            <div className="mt-3 space-y-3">
              {mockPlayers.slice(0, 2).map((p) => (
                <div key={p.id} className="flex items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-3">
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-white truncate">{p.firstName} {p.lastName}</div>
                    <div className="text-xs text-text-muted">{p.position}</div>
                  </div>
                  <div className="text-xs text-text-muted">{(p.developmentVelocity ?? 0).toFixed(2)}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

