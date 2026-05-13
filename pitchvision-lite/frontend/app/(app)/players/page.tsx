"use client";

import React, { useMemo, useState } from "react";

import { mockPlayers } from "@/data/demo";
import { useAppStore } from "@/lib/appStore";
import type { Player } from "@/types/domain";

import { FilterBar } from "@/components/ui/FilterBar";
import { PlayerCard } from "@/components/cards/PlayerCard";
import { EmptyState } from "@/components/ui/EmptyState";

export default function PlayersPage() {
  const { teamId } = useAppStore();
  const [q, setQ] = useState("");

  const players = useMemo(() => {
    return mockPlayers
      .filter((p) => p.teamId === teamId)
      .filter((p) => {
        if (!q) return true;
        const hay = `${p.firstName} ${p.lastName} ${p.position}`.toLowerCase();
        return hay.includes(q.toLowerCase());
      });
  }, [q, teamId]);

  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm font-medium text-emerald-200/80">Oyuncular</div>
        <h1 className="mt-1 text-2xl font-semibold text-white">Oyuncu listesi</h1>
        <p className="mt-2 text-sm text-text-muted">Demo performans & pasaport alanları mock veriden gelir.</p>
      </div>

      <FilterBar
        left={
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="w-72 max-w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40 transition-all"
            placeholder="Oyuncu / pozisyon ara..."
          />
        }
        right={<div className="text-sm text-text-muted">Toplam: {players.length}</div>}
      />

      {players.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {players.map((p) => (
            <PlayerCard key={p.id} player={p as Player} />
          ))}
        </div>
      ) : (
        <EmptyState
          title="Oyuncu bulunamadı"
          description={q ? `"${q}" aramasına uygun oyuncu bulunamadı.` : "Henüz bu takımda kayıtlı oyuncu bulunmuyor."}
          icon="👥"
          action={q ? (
            <button onClick={() => setQ("")} className="px-4 py-2 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-500 transition-all">
              Aramayı Temizle
            </button>
          ) : undefined}
        />
      )}
    </div>
  );
}

