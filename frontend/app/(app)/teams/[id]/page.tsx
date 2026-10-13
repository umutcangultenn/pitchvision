"use client";

import React, { useEffect, useState, useMemo } from "react";
import { useParams } from "next/navigation";

import { apiGetSettingsTeams, apiGetScoutingPlayers } from "@/lib/api";
import type { Team, Player } from "@/types/domain";

import { PlayerCard } from "@/components/cards/PlayerCard";

import { ErrorState } from "@/components/ui/ErrorState";

export default function TeamDetailPage() {
  const params = useParams();
  const teamId = Number(params.id);
  
  const [team, setTeam] = useState<Team | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Takımları getir
        const teamsResult = await apiGetSettingsTeams();
        if (teamsResult && Array.isArray(teamsResult)) {
          const foundTeam = teamsResult.find((t: any) => t.id === teamId);
          if (foundTeam) {
            setTeam({
              id: foundTeam.id,
              name: foundTeam.name,
              ageCategory: foundTeam.age_category,
              gameFormat: foundTeam.game_format,
              defaultFormation: foundTeam.default_formation,
              pitchLength: foundTeam.pitch_length,
              pitchWidth: foundTeam.pitch_width,
              season: foundTeam.season,
            } as Team);
          }
        }
        
        // Oyunculuları getir
        const playersResult = await apiGetScoutingPlayers(teamId);
        if (playersResult.ok) {
          setPlayers(playersResult.data);
        }
      } catch (error) {
        console.error("Takım verisi yükleme hatası:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [teamId]);

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-10 rounded-xl bg-white/5 w-64" />
        <div className="grid gap-4 md:grid-cols-3">
          {[...Array(3)].map((_, i) => <div key={i} className="h-20 rounded-2xl bg-white/5" />)}
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {[...Array(4)].map((_, i) => <div key={i} className="h-32 rounded-2xl bg-white/5" />)}
        </div>
      </div>
    );
  }

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

