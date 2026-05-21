"use client";

import React, { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { apiGetDrills, apiGetDrillsStats } from "@/lib/api";
import type { DrillRecommendation } from "@/types/domain";

export default function DrillsPage() {
  const [drills, setDrills] = useState<DrillRecommendation[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searchQ, setSearchQ] = useState("");
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>("");

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Antrenmanları getir
        const drillsResult = await apiGetDrills(undefined, undefined, selectedDifficulty || undefined);
        if (drillsResult.ok) {
          setDrills(drillsResult.data);
        }
        
        // İstatistikleri getir
        const statsResult = await apiGetDrillsStats();
        if (statsResult.ok) {
          setStats(statsResult.data);
        }
      } catch (error) {
        console.error("Drills verisi yükleme hatası:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedDifficulty]);

  // Filtreleme
  const filteredDrills = useMemo(() => {
    return drills.filter(d => {
      if (searchQ && !`${d.title} ${d.description}`.toLowerCase().includes(searchQ.toLowerCase())) return false;
      return true;
    });
  }, [drills, searchQ]);

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-10 rounded-xl bg-white/5 w-64" />
        {[...Array(3)].map((_, i) => <div key={i} className="h-32 rounded-2xl bg-white/5" />)}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Antrenman Önerileri</h1>
          <p className="text-sm text-text-muted mt-1">Taktiksel sorunları çözmek için antrenmanlar</p>
        </div>
      </div>

      {/* İstatistikler */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="rounded-xl bg-white/5 border border-white/10 p-4">
            <div className="text-xs text-text-muted">Toplam Antrenman</div>
            <div className="text-2xl font-bold text-emerald-400 mt-2">{stats.total_drills}</div>
          </div>
          <div className="rounded-xl bg-white/5 border border-white/10 p-4">
            <div className="text-xs text-text-muted">Kolay</div>
            <div className="text-2xl font-bold text-emerald-400 mt-2">{stats.by_difficulty?.easy || 0}</div>
          </div>
          <div className="rounded-xl bg-white/5 border border-white/10 p-4">
            <div className="text-xs text-text-muted">Orta</div>
            <div className="text-2xl font-bold text-emerald-400 mt-2">{stats.by_difficulty?.medium || 0}</div>
          </div>
          <div className="rounded-xl bg-white/5 border border-white/10 p-4">
            <div className="text-xs text-text-muted">Zor</div>
            <div className="text-2xl font-bold text-emerald-400 mt-2">{stats.by_difficulty?.hard || 0}</div>
          </div>
        </div>
      )}

      {/* Filtreler */}
      <div className="flex gap-3 flex-wrap">
        <input
          type="text"
          placeholder="Antrenman ara..."
          value={searchQ}
          onChange={(e) => setSearchQ(e.target.value)}
          className="flex-1 min-w-[200px] rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
        />
        
        <select
          value={selectedDifficulty}
          onChange={(e) => setSelectedDifficulty(e.target.value)}
          className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
        >
          <option value="">Tüm Zorluklar</option>
          <option value="easy">Kolay</option>
          <option value="medium">Orta</option>
          <option value="hard">Zor</option>
        </select>
      </div>

      {/* Antrenman Listesi */}
      <div className="grid gap-4 md:grid-cols-2">
        {filteredDrills.map(drill => (
          <Link key={drill.id} href={`/drills/${drill.id}`}>
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 hover:bg-white/10 transition cursor-pointer h-full">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-white">{drill.title}</h3>
                  <p className="text-xs text-text-muted mt-1">{drill.description}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                    drill.difficulty === "easy" ? "bg-green-500/20 text-green-300" :
                    drill.difficulty === "medium" ? "bg-yellow-500/20 text-yellow-300" :
                    "bg-red-500/20 text-red-300"
                  }`}>
                    {drill.difficulty === "easy" ? "Kolay" : drill.difficulty === "medium" ? "Orta" : "Zor"}
                  </span>
                </div>
              </div>
              
              <div className="mt-4 flex items-center justify-between text-xs text-text-muted">
                <span>⏱️ {drill.durationMinutes} dakika</span>
                <span>🏷️ {drill.problemType}</span>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {filteredDrills.length === 0 && (
        <div className="rounded-xl border border-white/10 bg-white/5 p-8 text-center">
          <p className="text-text-muted">Antrenman bulunamadı</p>
        </div>
      )}
    </div>
  );
}
