"use client";

import React, { useMemo } from "react";
import { useParams } from "next/navigation";

import { mockPlayers, mockTeams } from "@/data/demo";
import type { Team } from "@/types/domain";

import { PlayerCard } from "@/components/cards/PlayerCard";

import { ErrorState } from "@/components/ui/ErrorState";

export default function TeamDetailPage() {
  const params = useParams();
  const teamId = Number(params.id);

  const team = useMemo(() => mockTeams.find((t) => t.id === teamId), [teamId]);
  const players = useMemo(() => mockPlayers.filter((p) => p.teamId === teamId), [teamId]);

  if (!team) return <ErrorState title="Takım bulunamadı" description="Lütfen tekrar deneyin." />;

  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm font-medium text-emerald-200/80">Takımlar</div>
        <h1 className="mt-1 text-2xl font-semibold text-white">{team.name}</h1>
        <p className="mt-2 text-sm text-text-muted">
          {team.ageCategory} • {team.gameFormat} • Dizilim: {team.defaultFormation}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl pv-card p-5">
          <div className="text-xs text-text-muted">Sezon</div>
          <div className="mt-1 text-lg font-semibold text-white">{team.season}</div>
        </div>
        <div className="rounded-2xl pv-card p-5">
          <div className="text-xs text-text-muted">Saha</div>
          <div className="mt-1 text-lg font-semibold text-white">
            {team.pitchLength}x{team.pitchWidth}m
          </div>
        </div>
        <div className="rounded-2xl pv-card p-5">
          <div className="text-xs text-text-muted">Oyuncu</div>
          <div className="mt-1 text-lg font-semibold text-white">{players.length}</div>
        </div>
      </div>

      <div>
        <div className="mb-3 text-sm font-semibold text-white">Takım kadrosu</div>
        <div className="grid gap-4 md:grid-cols-2">
          {players.map((p) => (
            <PlayerCard key={p.id} player={p as any} />
          ))}
        </div>
      </div>
    </div>
  );
}

