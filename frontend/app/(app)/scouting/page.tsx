"use client";

import React, { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { apiGetScoutingPlayers, apiGetScoutingNotes, apiGetScoutingStats } from "@/lib/api";
import { useAppStore } from "@/lib/appStore";
import type { Player, ScoutNote } from "@/types/domain";

export default function ScoutingPage() {
  const { teamId } = useAppStore();
  const [players, setPlayers] = useState<Player[]>([]);
  const [notes, setNotes] = useState<Record<number, ScoutNote[]>>({});
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searchQ, setSearchQ] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Oyuncu listesini getir
        const playersResult = await apiGetScoutingPlayers(teamId || undefined);
        if (playersResult.ok) {
          setPlayers(playersResult.data);
          
          // Her oyuncu için notları getir
          for (const player of playersResult.data) {
            const notesResult = await apiGetScoutingNotes(player.id);
            if (notesResult.ok) {
              setNotes(prev => ({
                ...prev,
                [player.id]: notesResult.data
              }));
            }
          }
        }
        
        // İstatistikleri getir
        const statsResult = await apiGetScoutingStats(teamId || undefined);
        if (statsResult.ok) {
          setStats(statsResult.data);
        }
      } catch (error) {
        console.error("Scouting verisi yükleme hatası:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [teamId]);

  // Filtreleme
  const filteredPlayers = useMemo(() => {
    return players.filter(p => {
      if (searchQ && !`${p.firstName} ${p.lastName}`.toLowerCase().includes(searchQ.toLowerCase())) return false;
      return true;
    });
  }, [players, searchQ]);

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-10 rounded-xl bg-white/5 w-64" />
        {[...Array(3)].map((_, i) => <div key={i} className="h-24 rounded-2xl bg-white/5" />)}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Oyuncu İzleme</h1>
          <p className="text-sm text-text-muted mt-1">Takım oyuncularını izle ve değerlendir</p>
        </div>
      </div>

      {/* İstatistikler */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="rounded-xl bg-white/5 border border-white/10 p-4">
            <div className="text-xs text-text-muted">Toplam Oyuncu</div>
            <div className="text-2xl font-bold text-emerald-400 mt-2">{stats.total_players}</div>
          </div>
          <div className="rounded-xl bg-white/5 border border-white/10 p-4">
            <div className="text-xs text-text-muted">Yüksek Potansiyel</div>
            <div className="text-2xl font-bold text-emerald-400 mt-2">{stats.high_potential}</div>
          </div>
          <div className="rounded-xl bg-white/5 border border-white/10 p-4">
            <div className="text-xs text-text-muted">Yüksek Hız</div>
            <div className="text-2xl font-bold text-emerald-400 mt-2">{stats.high_velocity}</div>
          </div>
          <div className="rounded-xl bg-white/5 border border-white/10 p-4">
            <div className="text-xs text-text-muted">Ort. Gelişim Hızı</div>
            <div className="text-2xl font-bold text-emerald-400 mt-2">{stats.average_velocity?.toFixed(2)}</div>
          </div>
        </div>
      )}

      {/* Arama */}
      <div>
        <input
          type="text"
          placeholder="Oyuncu ara..."
          value={searchQ}
          onChange={(e) => setSearchQ(e.target.value)}
          className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
        />
      </div>

      {/* Oyuncu Listesi */}
      <div className="space-y-3">
        {filteredPlayers.map(player => (
          <Link key={player.id} href={`/players/${player.id}`}>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-white">{player.firstName} {player.lastName}</h3>
                  <p className="text-xs text-text-muted mt-1">{player.position} • Gelişim: {player.developmentVelocity?.toFixed(2)}</p>
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold text-emerald-400">{notes[player.id]?.length || 0} not</div>
                  <div className="text-xs text-text-muted mt-1">Teknik: {player.technicalScore?.toFixed(1)}</div>
                </div>
              </div>
              
              {/* Notlar */}
              {notes[player.id] && notes[player.id].length > 0 && (
                <div className="mt-3 space-y-2 border-t border-white/10 pt-3">
                  {notes[player.id].slice(0, 2).map(note => (
                    <div key={note.id} className="text-xs text-text-muted">
                      <span className="text-emerald-400">•</span> {note.note}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Link>
        ))}
      </div>

      {filteredPlayers.length === 0 && (
        <div className="rounded-xl border border-white/10 bg-white/5 p-8 text-center">
          <p className="text-text-muted">Oyuncu bulunamadı</p>
        </div>
      )}
    </div>
  );
}
