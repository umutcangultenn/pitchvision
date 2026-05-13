"use client";

import Link from "next/link";
import React from "react";

import type { Match, VideoAsset } from "@/types/domain";
import { StatusBadge } from "@/components/ui/StatusBadge";

export type MatchUiStatus =
  | "Analiz tamamlandı"
  | "Kalibrasyon bekliyor"
  | "İşleniyor"
  | "Hata";

export function MatchListCard({
  match,
  teamName,
  video,
  uiStatus,
  teamLengthM,
  compactnessM,
  alertCount,
}: {
  match: Match;
  teamName: string;
  video?: VideoAsset;
  uiStatus: MatchUiStatus;
  teamLengthM?: number;
  compactnessM?: number;
  alertCount: number;
}) {
  const statusTone =
    uiStatus === "Analiz tamamlandı"
      ? "completed"
      : uiStatus === "İşleniyor"
      ? "processing"
      : uiStatus === "Kalibrasyon bekliyor"
      ? "scheduled"
      : "failed";

  const durationLabel = video?.durationSeconds
    ? `${Math.round(video.durationSeconds / 60)} dk`
    : "—";

  return (
    <div className="rounded-2xl pv-card p-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="truncate text-base font-semibold text-white">
              {teamName} vs {match.opponentName}
            </h3>
            <StatusBadge status={statusTone} />
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-text-muted">
              {uiStatus}
            </span>
          </div>

          <div className="mt-2 flex flex-wrap gap-2 text-sm text-text-muted">
            <span>{new Date(match.matchDate).toLocaleDateString("tr-TR")}</span>
            <span className="opacity-60">•</span>
            <span>{match.ageCategory}</span>
            <span className="opacity-60">•</span>
            <span>{match.gameFormat}</span>
            <span className="opacity-60">•</span>
            <span>Video: {durationLabel}</span>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div className="rounded-xl border border-white/10 bg-white/5 p-3">
              <div className="text-xs text-text-muted">Skor</div>
              <div className="mt-1 text-base font-semibold text-white">
                {match.scoreFor}:{match.scoreAgainst}
              </div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-3">
              <div className="text-xs text-text-muted">Takım boyu</div>
              <div className="mt-1 text-base font-semibold text-white">
                {typeof teamLengthM === "number" ? `${teamLengthM.toFixed(1)} m` : "—"}
              </div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-3">
              <div className="text-xs text-text-muted">Kompaktlık</div>
              <div className="mt-1 text-base font-semibold text-white">
                {typeof compactnessM === "number" ? `${compactnessM.toFixed(1)} m` : "—"}
              </div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-3">
              <div className="text-xs text-text-muted">Uyarı</div>
              <div className="mt-1 text-base font-semibold text-white">{alertCount}</div>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 lg:flex-col lg:items-end">
          <Link
            href={`/matches/${match.id}/analysis`}
            className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
          >
            Analizi Aç
          </Link>
          <Link
            href={`/matches/${match.id}/report`}
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-text-muted hover:text-white hover:border-emerald-400/40"
          >
            Raporu Gör
          </Link>
          <Link
            href={`/matches/${match.id}/calibration`}
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-text-muted hover:text-white hover:border-emerald-400/40"
          >
            Kalibrasyon
          </Link>
          <Link
            href={`/matches/${match.id}/analysis#clips`}
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-text-muted hover:text-white hover:border-emerald-400/40"
          >
            Klipler
          </Link>
        </div>
      </div>
    </div>
  );
}

