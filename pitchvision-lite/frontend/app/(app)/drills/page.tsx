"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";

import { mockDrills } from "@/data/demo";
import { DrillRecommendationCard } from "@/components/cards/DrillRecommendationCard";
import type { AlertType, ProblemType, DrillDifficulty, PitchSize } from "@/types/domain";

type FilterProblem = "compactness" | "block_gap" | "transition" | "depth_run" | "support_run" | "pressing";
type FilterDifficulty = "easy" | "medium" | "hard";

// Problem type mapping (constant, outside component)
const PROBLEM_MAP: Record<FilterProblem, { name: string; alerts: AlertType[] }> = {
  compactness: { name: "Savunma Kompaktlığı", alerts: ["compactness_lost"] },
  block_gap: { name: "Bloklar Arası Mesafe", alerts: ["block_gap_wide"] },
  transition: { name: "Geçiş Savunması", alerts: ["transition_slow"] },
  depth_run: { name: "Derin Koşu", alerts: ["depth_run_opportunity"] },
  support_run: { name: "Destek Açısı", alerts: ["line_breaking_pass"] },
  pressing: { name: "Pres", alerts: ["pressing"] },
};

export default function DrillsPage() {
  const [searchQ, setSearchQ] = useState("");
  const [selectedProblems, setSelectedProblems] = useState<FilterProblem[]>([]);
  const [selectedAgeCategory, setSelectedAgeCategory] = useState<string>("");
  const [minDuration, setMinDuration] = useState(5);
  const [maxDuration, setMaxDuration] = useState(60);
  const [minPlayers, setMinPlayers] = useState(0);
  const [maxPlayers, setMaxPlayers] = useState(30);
  const [selectedDifficulty, setSelectedDifficulty] = useState<FilterDifficulty | "">("");
  const [appliedDrills, setAppliedDrills] = useState<number[]>([]);

  // Filter drills
  const filteredDrills = useMemo(() => {
    return mockDrills.filter((d) => {
      if (searchQ && !`${d.title} ${d.problemType}`.toLowerCase().includes(searchQ.toLowerCase())) return false;
      if (selectedProblems.length && !selectedProblems.some((p) => PROBLEM_MAP[p].alerts.includes(d.alertType))) return false;
      if (selectedAgeCategory && d.ageCategory !== selectedAgeCategory) return false;
      if (d.durationMinutes < minDuration || d.durationMinutes > maxDuration) return false;
      if (d.playerCount < minPlayers || d.playerCount > maxPlayers) return false;
      if (selectedDifficulty && d.difficulty !== selectedDifficulty) return false;
      return true;
    });
  }, [searchQ, selectedProblems, selectedAgeCategory, minDuration, maxDuration, minPlayers, maxPlayers, selectedDifficulty]);

  // Statistics
  const stats = {
    thisWeek: 8,
    mostCommon: "Bloklar arası kopukluk",
    relatedMatches: 4,
    applied: appliedDrills.length,
  };

  return (
    <div className="space-y-6">
      {/* ── Header ── */}
      <div>
        <div className="text-sm font-medium text-emerald-200/80">Antrenman Önerileri</div>
        <h1 className="mt-1 text-3xl font-bold text-white">Antrenman Önerileri</h1>
        <p className="mt-2 text-sm text-text-muted">Maç analizlerinden çıkan bulgulara göre önerilen antrenman içerikleri.</p>
      </div>

      {/* ── Stats ── */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Bu Hafta Önerilen Drill", value: stats.thisWeek, icon: "📋" },
          { label: "En Sık Problem", value: stats.mostCommon, icon: "⚠️" },
          { label: "İlgili Maç Sayısı", value: stats.relatedMatches, icon: "⚽" },
          { label: "Uygulandı", value: stats.applied, icon: "✅" },
        ].map((s) => (
          <div key={s.label} className="rounded-2xl pv-card p-5">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-text-muted">{s.label}</div>
                <div className="mt-2 text-2xl font-bold text-white">{s.value}</div>
              </div>
              <div className="text-3xl">{s.icon}</div>
            </div>
          </div>
        ))}
      </div>

      {/* ── Filters + List ── */}
      <div className="grid gap-6 lg:grid-cols-4">
        {/* ── Left: Filters ── */}
        <div className="rounded-2xl pv-card p-5 space-y-4 lg:col-span-1">
          <div className="text-sm font-semibold text-white">Filtreler</div>

          <input
            value={searchQ}
            onChange={(e) => setSearchQ(e.target.value)}
            placeholder="Drill ara..."
            className="w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm text-white placeholder:text-text-muted outline-none focus:ring-2 focus:ring-accent/40"
          />

          <div>
            <label className="text-xs text-text-muted mb-2 block">Problem Tipi</label>
            <div className="flex flex-col gap-2">
              {Object.entries(PROBLEM_MAP).map(([key, { name }]) => (
                <button
                  key={key}
                  onClick={() => setSelectedProblems((s) => (s.includes(key as FilterProblem) ? s.filter((x) => x !== key) : [...s, key as FilterProblem]))}
                  className={`text-left text-xs px-2.5 py-1.5 rounded-lg transition-all border ${
                    selectedProblems.includes(key as FilterProblem)
                      ? "bg-accent/20 border-accent/40 text-accent"
                      : "bg-white/5 border-white/10 text-text-muted hover:bg-white/10"
                  }`}
                >
                  {name}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs text-text-muted mb-2 block">Yaş Kategorisi</label>
            <select value={selectedAgeCategory} onChange={(e) => setSelectedAgeCategory(e.target.value)} className="w-full rounded-lg bg-white/5 border border-white/10 px-2 py-1.5 text-xs text-white outline-none focus:ring-2 focus:ring-accent/40">
              <option value="">Tümü</option>
              <option value="U15">U15</option>
              <option value="U17">U17</option>
              <option value="U19">U19</option>
              <option value="Senior">Senior</option>
            </select>
          </div>

          <div>
            <label className="text-xs text-text-muted mb-2 block">Süre (dakika)</label>
            <div className="flex gap-2">
              <input type="number" min={5} max={60} value={minDuration} onChange={(e) => setMinDuration(Number(e.target.value))} className="w-1/2 rounded-lg bg-white/5 border border-white/10 px-2 py-1.5 text-xs text-white outline-none focus:ring-2 focus:ring-accent/40" />
              <input type="number" min={5} max={60} value={maxDuration} onChange={(e) => setMaxDuration(Number(e.target.value))} className="w-1/2 rounded-lg bg-white/5 border border-white/10 px-2 py-1.5 text-xs text-white outline-none focus:ring-2 focus:ring-accent/40" />
            </div>
          </div>

          <div>
            <label className="text-xs text-text-muted mb-2 block">Oyuncu Sayısı</label>
            <div className="flex gap-2">
              <input type="number" min={0} max={30} value={minPlayers} onChange={(e) => setMinPlayers(Number(e.target.value))} className="w-1/2 rounded-lg bg-white/5 border border-white/10 px-2 py-1.5 text-xs text-white outline-none focus:ring-2 focus:ring-accent/40" />
              <input type="number" min={0} max={30} value={maxPlayers} onChange={(e) => setMaxPlayers(Number(e.target.value))} className="w-1/2 rounded-lg bg-white/5 border border-white/10 px-2 py-1.5 text-xs text-white outline-none focus:ring-2 focus:ring-accent/40" />
            </div>
          </div>

          <div>
            <label className="text-xs text-text-muted mb-2 block">Zorluk</label>
            <div className="flex flex-col gap-2">
              {["easy", "medium", "hard"].map((d) => (
                <button
                  key={d}
                  onClick={() => setSelectedDifficulty(selectedDifficulty === d ? "" : (d as FilterDifficulty))}
                  className={`text-left text-xs px-2.5 py-1.5 rounded-lg transition-all border ${
                    selectedDifficulty === d
                      ? "bg-accent/20 border-accent/40 text-accent"
                      : "bg-white/5 border-white/10 text-text-muted hover:bg-white/10"
                  }`}
                >
                  {d === "easy" ? "Kolay" : d === "medium" ? "Orta" : "Zor"}
                </button>
              ))}
            </div>
          </div>

          <button onClick={() => { setSearchQ(""); setSelectedProblems([]); setSelectedAgeCategory(""); setMinDuration(5); setMaxDuration(60); setMinPlayers(0); setMaxPlayers(30); setSelectedDifficulty(""); }} className="w-full px-3 py-2 rounded-lg text-xs font-medium bg-white/5 border border-white/10 text-text-muted hover:bg-white/10 transition-all">
            Filtreleri Temizle
          </button>
        </div>

        {/* ── Right: Drills ── */}
        <div className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-sm font-semibold text-white">Antrenman Drilleri ({filteredDrills.length})</div>
          </div>

          {filteredDrills.length === 0 ? (
            <div className="rounded-2xl pv-card p-8 text-center">
              <div className="text-lg text-text-muted">Filtrelere uygun drill bulunamadı.</div>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {filteredDrills.map((d) => (
                <div key={d.id} className="relative">
                  <DrillRecommendationCard
                    drill={d}
                    isApplied={appliedDrills.includes(d.id)}
                    onMarkApplied={() => setAppliedDrills((prev) => (prev.includes(d.id) ? prev.filter((x) => x !== d.id) : [...prev, d.id]))}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── Disclaimer ── */}
      <div className="rounded-xl bg-blue-500/5 border border-blue-500/20 p-4 text-sm text-blue-300/80">
        ℹ️ Bu antrenman önerileri maç analiz verilerine dayanmaktadır. Takımınızın ihtiyaçlarına göre koç tarafından uyarlanabilir.
      </div>
    </div>
  );
}
