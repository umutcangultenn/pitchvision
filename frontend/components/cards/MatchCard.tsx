"use client";

import Link from "next/link";
import React from "react";

import type { Match } from "@/types/domain";
import { StatusBadge } from "@/components/ui/StatusBadge";

export function MatchCard({
  match,
  detailHref,
}: {
  match: Match;
  detailHref?: string;
}) {
  const href = detailHref ?? `/matches/${match.id}`;
  return (
    <div className="rounded-2xl pv-card p-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="truncate text-base font-semibold text-white">
              {match.opponentName}
            </h3>
            <StatusBadge status={match.status} />
          </div>
          <div className="mt-2 flex flex-wrap gap-2 text-sm text-text-muted">
            <span>{match.ageCategory}</span>
            <span className="opacity-60">•</span>
            <span>{match.gameFormat}</span>
            <span className="opacity-60">•</span>
            <span>{new Date(match.matchDate).toLocaleDateString("tr-TR")}</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-center">
            <div className="text-xs text-text-muted">Skor</div>
            <div className="mt-1 text-lg font-semibold text-white">
              {match.scoreFor}:{match.scoreAgainst}
            </div>
          </div>
          <Link
            href={href}
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-white transition hover:border-emerald-400/40"
          >
            Detay
          </Link>
        </div>
      </div>
    </div>
  );
}

