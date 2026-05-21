"use client";

import React from "react";

import type { Player } from "@/types/domain";

import { StatusBadge } from "@/components/ui/StatusBadge";

export function PlayerCard({ player }: { player: Player }) {
  const fullName = `${player.firstName} ${player.lastName}`;
  return (
    <div className="rounded-2xl pv-card p-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div className="min-w-0">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl border border-white/10 bg-white/5" />
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold text-white">{fullName}</div>
              <div className="mt-1 flex flex-wrap gap-2 text-xs text-text-muted">
                <span>{player.position}</span>
                <span className="opacity-60">•</span>
                <span>{player.dominantFoot}</span>
              </div>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <div className="rounded-xl border border-white/10 bg-white/5 p-3">
              <div className="text-xs text-text-muted">Teknik</div>
              <div className="mt-1 text-base font-semibold text-white">
                {player.technicalScore?.toFixed(1) ?? "—"}
              </div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-3">
              <div className="text-xs text-text-muted">Taktik</div>
              <div className="mt-1 text-base font-semibold text-white">
                {player.tacticalScore?.toFixed(1) ?? "—"}
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col items-start gap-2 md:items-end">
          <div className="text-xs text-text-muted">Gelişim hızı</div>
          <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-center">
            <div className="text-lg font-semibold text-white">{(player.developmentVelocity ?? 0).toFixed(2)}</div>
          </div>
          <StatusBadge status="active" />
        </div>
      </div>
    </div>
  );
}

