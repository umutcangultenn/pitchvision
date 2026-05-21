"use client";

import React, { useState } from "react";
import type { Player, PlayerMatchPerformance } from "@/types/domain";
import { EmptyState } from "@/components/ui/EmptyState";

type PlayersTabProps = {
  players: Player[];
  performances: PlayerMatchPerformance[];
  onOpenPlayerProfile?: (playerId: number) => void;
};

export function PlayersTab({ players, performances, onOpenPlayerProfile }: PlayersTabProps) {
  const [sortBy, setSortBy] = useState<"name" | "alerts" | "speed" | "score">("alerts");

  const getPerformance = (playerId: number) => {
    return performances.find(p => p.playerId === playerId);
  };

  const sortedPlayers = [...players].sort((a, b) => {
    const perfA = getPerformance(a.id);
    const perfB = getPerformance(b.id);

    switch (sortBy) {
      case "name":
        return `${a.firstName} ${a.lastName}`.localeCompare(`${b.firstName} ${b.lastName}`);
      case "alerts":
        return (perfB?.alertsInvolved || 0) - (perfA?.alertsInvolved || 0);
      case "speed":
        return (perfB?.maxSpeed || 0) - (perfA?.maxSpeed || 0);
      case "score":
        return (perfB?.tacticalScore || 0) - (perfA?.tacticalScore || 0);
      default:
        return 0;
    }
  });

  const getPositionColor = (position: string) => {
    if (position.includes("GK")) return "bg-warning/20 text-warning border-warning/30";
    if (position.includes("CB") || position.includes("LB") || position.includes("RB")) return "bg-danger/20 text-danger border-danger/30";
    if (position.includes("CM") || position.includes("DM") || position.includes("AM")) return "bg-accent/20 text-accent border-accent/30";
    if (position.includes("LW") || position.includes("RW") || position.includes("CF")) return "bg-success/20 text-success border-success/30";
    return "bg-white/10 text-text-muted border-white/20";
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold text-white">Oyuncu Performansları</div>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className="px-3 py-1.5 rounded-lg text-xs bg-white/10 border border-white/20 text-text"
        >
          <option value="alerts">Uyarı Sayısı</option>
          <option value="speed">Maks Hız</option>
          <option value="score">Taktiksel Skor</option>
          <option value="name">İsim</option>
        </select>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {sortedPlayers.length === 0 ? (
          <EmptyState
            title="Henüz oyuncu yok"
            description="Bu maç için oyuncu verisi bulunamadı."
            icon="👥"
          />
        ) : (
          sortedPlayers.map(player => {
          const performance = getPerformance(player.id);
          
          return (
            <div
              key={player.id}
              className="p-4 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 transition-all cursor-pointer"
              onClick={() => onOpenPlayerProfile?.(player.id)}
            >
              <div className="flex items-center gap-3">
                {/* Player avatar */}
                <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-semibold text-accent">
                    {player.firstName[0]}{player.lastName[0]}
                  </span>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="text-sm font-medium text-white">
                      {player.firstName} {player.lastName}
                    </div>
                    <span className={`text-xs px-2 py-1 rounded border ${getPositionColor(player.position)}`}>
                      {player.position}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div>
                      <span className="text-text-muted">Ortalama Pozisyon:</span>
                      <div className="text-white">
                        ({(performance?.averagePositionX || 0).toFixed(2)}, {(performance?.averagePositionY || 0).toFixed(2)})
                      </div>
                    </div>
                    <div>
                      <span className="text-text-muted">Maks Hız:</span>
                      <div className="text-white">{(performance?.maxSpeed || 0).toFixed(1)} km/h</div>
                    </div>
                    <div>
                      <span className="text-text-muted">Taktiksel Uyarı:</span>
                      <div className={`font-semibold ${
                        (performance?.alertsInvolved || 0) > 2 ? "text-danger" :
                        (performance?.alertsInvolved || 0) > 0 ? "text-warning" : "text-success"
                      }`}>
                        {performance?.alertsInvolved || 0} uyarı
                      </div>
                    </div>
                    <div>
                      <span className="text-text-muted">Taktiksel Skor:</span>
                      <div className="text-accent font-semibold">
                        {(performance?.tacticalScore || 0).toFixed(1)}/10
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex-shrink-0">
                  <button className="px-3 py-1.5 rounded-lg text-xs font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all">
                    📊 Pasaport
                  </button>
                </div>
              </div>

              {performance?.developmentNotes && (
                <div className="mt-3 p-3 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-xs text-text-muted mb-1">Gelişim Notu:</div>
                  <div className="text-xs text-white">{performance.developmentNotes}</div>
                </div>
              )}
            </div>
          );
        })
        )}
      </div>
    </div>
  );
}