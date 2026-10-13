"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import { LineChart, Line, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from "recharts";

import { mockPlayers, mockScoutingNotes, mockMatches } from "@/data/demo";
import { useAppStore } from "@/lib/appStore";
import type { Player } from "@/types/domain";

import { ScoutNoteCard } from "@/components/cards/ScoutNoteCard";
import { EmptyState } from "@/components/ui/EmptyState";

type SortBy = "name" | "score" | "velocity" | "age";
type FilterTag = "potential" | "watch" | "technical" | "physical" | "tactical" | "transfer";

export default function ScoutingPage() {
  const { teamId } = useAppStore();
  const [searchQ, setSearchQ] = useState("");
  const [sortBy, setSortBy] = useState<SortBy>("velocity");
  const [ageMin, setAgeMin] = useState(14);
  const [ageMax, setAgeMax] = useState(23);
  const [selectedPosition, setSelectedPosition] = useState<string>("");
  const [selectedTags, setSelectedTags] = useState<FilterTag[]>([]);
  const [minTactical, setMinTactical] = useState(0);
  const [minPhysical, setMinPhysical] = useState(0);
  const [selectedPlayers, setSelectedPlayers] = useState<number[]>([]);
  const [addingNote, setAddingNote] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [noteRating, setNoteRating] = useState(7.0);

  // Helpers
  const age = (birthDate: string) => {
    const bd = new Date(birthDate);
    const today = new Date();
    let a = today.getFullYear() - bd.getFullYear();
    if (today.getMonth() < bd.getMonth() || (today.getMonth() === bd.getMonth() && today.getDate() < bd.getDate())) a--;
    return a;
  };

  const overallScore = (p: Player) => {
    const scores = [p.technicalScore ?? 0, p.tacticalScore ?? 0, p.physicalScore ?? 0, p.decisionScore ?? 0];
    return scores.reduce((a, b) => a + b, 0) / scores.length;
  };

  // Filter & sort
  const allPlayers = useMemo(() => {
    return mockPlayers
      .filter((p) => p.teamId === teamId)
      .filter((p) => {
        const playerAge = age(p.birthDate);
        return playerAge >= ageMin && playerAge <= ageMax;
      })
      .filter((p) => !selectedPosition || p.position.toUpperCase().includes(selectedPosition.toUpperCase()))
      .filter((p) => (p.tacticalScore ?? 0) >= minTactical)
      .filter((p) => (p.physicalScore ?? 0) >= minPhysical)
      .filter((p) => (searchQ ? `${p.firstName} ${p.lastName} ${p.position}`.toLowerCase().includes(searchQ.toLowerCase()) : true))
      .filter((p) => {
        if (!selectedTags.length) return true;
        if (selectedTags.includes("potential") && (p.developmentVelocity ?? 0) > 1.0) return true;
        if (selectedTags.includes("watch") && (p.developmentVelocity ?? 0) > 0.5) return true;
        if (selectedTags.includes("technical") && (p.technicalScore ?? 0) >= 7) return true;
        if (selectedTags.includes("physical") && (p.physicalScore ?? 0) >= 7) return true;
        if (selectedTags.includes("tactical") && (p.tacticalScore ?? 0) < 6) return true;
        if (selectedTags.includes("transfer")) return true;
        return false;
      })
      .sort((a, b) => {
        if (sortBy === "name") return a.firstName.localeCompare(b.firstName);
        if (sortBy === "score") return overallScore(b) - overallScore(a);
        if (sortBy === "velocity") return (b.developmentVelocity ?? 0) - (a.developmentVelocity ?? 0);
        if (sortBy === "age") return age(a.birthDate) - age(b.birthDate);
        return 0;
      });
  }, [searchQ, sortBy, ageMin, ageMax, selectedPosition, selectedTags, minTactical, minPhysical, teamId]);

  const hiddenGems = useMemo(() => allPlayers.filter((p) => (p.developmentVelocity ?? 0) > 0.5), [allPlayers]);

  const stats = {
    watched: mockPlayers.filter((p) => p.teamId === teamId).length,
    highPotential: mockPlayers.filter((p) => (p.developmentVelocity ?? 0) > 1.0).length,
    highVelocity: mockPlayers.filter((p) => (p.developmentVelocity ?? 0) > 0.5).length,
    notes: mockScoutingNotes.length,
  };

  // Comparison data
  const selectedPlayerData = useMemo(() => allPlayers.filter((p) => selectedPlayers.includes(p.id)), [allPlayers, selectedPlayers]);

  const scatterData = useMemo(
    () =>
      allPlayers.map((p) => ({
        x: overallScore(p),
        y: p.developmentVelocity ?? 0,
        name: `${p.firstName} ${p.lastName}`,
        playerId: p.id,
      })),
    [allPlayers]
  );

  const radarData = useMemo(
    () =>
      selectedPlayerData.slice(0, 3).map((p) => ({
        player: `${p.firstName[0]}${p.lastName[0]}`,
        technical: (p.technicalScore ?? 0) / 10,
        tactical: (p.tacticalScore ?? 0) / 10,
        physical: (p.physicalScore ?? 0) / 10,
        decision: (p.decisionScore ?? 0) / 10,
        all: {
          technical: p.technicalScore ?? 0,
          tactical: p.tacticalScore ?? 0,
          physical: p.physicalScore ?? 0,
          decision: p.decisionScore ?? 0,
        },
      })),
    [selectedPlayerData]
  );

  const notes = useMemo(() => mockScoutingNotes.slice(0, 5), []);

  return (
    <div className="space-y-6">
      {/* ── Header ── */}
      <div>
        <div className="text-sm font-medium text-emerald-200/80">Scouting</div>
        <h1 className="mt-1 text-3xl font-bold text-white">Oyuncu Keşif & Analiz</h1>
        <p className="mt-2 text-sm text-text-muted">Oyuncuları yaş, pozisyon, skor ve gelişim ivmesine göre karşılaştır.</p>
      </div>

      {/* ── Stats ── */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "İzlenen Oyuncu", value: stats.watched, icon: "👀" },
          { label: "Yüksek Potansiyel", value: stats.highPotential, icon: "⭐" },
          { label: "Gelişim Hızı Yüksek", value: stats.highVelocity, icon: "📈" },
          { label: "Scout Notu", value: stats.notes, icon: "📝" },
        ].map((s) => (
          <div key={s.label} className="rounded-2xl pv-card p-5">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-text-muted">{s.label}</div>
                <div className="mt-2 text-3xl font-bold text-white">{s.value}</div>
              </div>
              <div className="text-4xl">{s.icon}</div>
            </div>
          </div>
        ))}
      </div>

      {/* ── Main content ── */}
      <div className="grid gap-6 lg:grid-cols-4">
        {/* ── Left: Table ── */}
        <div className="lg:col-span-2 space-y-4">
          {/* ── Filters ── */}
          <div className="rounded-2xl pv-card p-5 space-y-4">
            <div className="text-sm font-semibold text-white">Filtreler</div>

            <input
              value={searchQ}
              onChange={(e) => setSearchQ(e.target.value)}
              placeholder="Oyuncu ara..."
              className="w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm text-white placeholder:text-text-muted outline-none focus:ring-2 focus:ring-accent/40"
            />

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-text-muted">Yaş Min</label>
                <input type="number" min={14} max={30} value={ageMin} onChange={(e) => setAgeMin(Number(e.target.value))} className="w-full mt-1 rounded-lg bg-white/5 border border-white/10 px-2 py-1 text-xs text-white outline-none focus:ring-2 focus:ring-accent/40" />
              </div>
              <div>
                <label className="text-xs text-text-muted">Yaş Max</label>
                <input type="number" min={14} max={30} value={ageMax} onChange={(e) => setAgeMax(Number(e.target.value))} className="w-full mt-1 rounded-lg bg-white/5 border border-white/10 px-2 py-1 text-xs text-white outline-none focus:ring-2 focus:ring-accent/40" />
              </div>
            </div>

            <div>
              <label className="text-xs text-text-muted">Pozisyon</label>
              <select value={selectedPosition} onChange={(e) => setSelectedPosition(e.target.value)} className="w-full mt-1 rounded-lg bg-white/5 border border-white/10 px-2 py-1.5 text-xs text-white outline-none focus:ring-2 focus:ring-accent/40">
                <option value="">Tümü</option>
                <option value="CB">Stoper</option>
                <option value="LB">Sol Bek</option>
                <option value="RB">Sağ Bek</option>
                <option value="CM">Orta Saha</option>
                <option value="LW">Sol Kanat</option>
                <option value="RW">Sağ Kanat</option>
                <option value="ST">Forvet</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-text-muted">Min Taktik</label>
                <input type="range" min={0} max={10} step={0.5} value={minTactical} onChange={(e) => setMinTactical(Number(e.target.value))} className="w-full mt-1" />
                <div className="text-xs text-accent font-bold mt-1">{minTactical.toFixed(1)}</div>
              </div>
              <div>
                <label className="text-xs text-text-muted">Min Fizik</label>
                <input type="range" min={0} max={10} step={0.5} value={minPhysical} onChange={(e) => setMinPhysical(Number(e.target.value))} className="w-full mt-1" />
                <div className="text-xs text-accent font-bold mt-1">{minPhysical.toFixed(1)}</div>
              </div>
            </div>

            <div>
              <label className="text-xs text-text-muted mb-2 block">Etiketler</label>
              <div className="flex flex-wrap gap-2">
                {["potential", "watch", "technical", "physical", "tactical", "transfer"].map((tag) => (
                  <button
                    key={tag}
                    onClick={() => setSelectedTags((t) => (t.includes(tag as FilterTag) ? t.filter((x) => x !== tag) : [...t, tag as FilterTag]))}
                    className={`text-xs px-2.5 py-1.5 rounded-lg transition-all border ${
                      selectedTags.includes(tag as FilterTag)
                        ? "bg-accent/20 border-accent/40 text-accent"
                        : "bg-white/5 border-white/10 text-text-muted hover:bg-white/10"
                    }`}
                  >
                    {tag === "potential" ? "Potansiyel" : tag === "watch" ? "İzlenmeli" : tag === "technical" ? "Teknik Güçlü" : tag === "physical" ? "Fiziksel Güçlü" : tag === "tactical" ? "Taktik Gelişmeli" : "Transfer Adayı"}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs text-text-muted">Sırala</label>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value as SortBy)} className="w-full mt-1 rounded-lg bg-white/5 border border-white/10 px-2 py-1.5 text-xs text-white outline-none focus:ring-2 focus:ring-accent/40">
                <option value="velocity">Gelişim Hızı ↓</option>
                <option value="score">Skor ↓</option>
                <option value="age">Yaş ↑</option>
                <option value="name">Ad A-Z</option>
              </select>
            </div>
          </div>

          {/* ── Player Table ── */}
          <div className="rounded-2xl pv-card p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold text-white">Oyuncu Listesi ({allPlayers.length})</div>
              <div className="text-xs text-accent">Seçili: {selectedPlayers.length}</div>
            </div>

            {allPlayers.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-2 px-2"><input type="checkbox" className="w-4 h-4" onChange={(e) => setSelectedPlayers(e.target.checked ? allPlayers.map((p) => p.id) : [])} /></th>
                      <th className="text-left py-2 px-2 text-text-muted">Oyuncu</th>
                      <th className="text-right py-2 px-2 text-text-muted">Yaş</th>
                      <th className="text-right py-2 px-2 text-text-muted">Skor</th>
                      <th className="text-right py-2 px-2 text-text-muted">İvme</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allPlayers.slice(0, 20).map((p) => (
                      <tr key={p.id} className="border-b border-white/5 hover:bg-white/3 transition-all">
                        <td className="py-2 px-2">
                          <input
                            type="checkbox"
                            className="w-4 h-4"
                            checked={selectedPlayers.includes(p.id)}
                            onChange={(e) => setSelectedPlayers((s) => (e.target.checked ? [...s, p.id] : s.filter((x) => x !== p.id)))}
                          />
                        </td>
                        <td className="py-2 px-2 text-white font-medium">
                          <Link href={`/players/${p.id}`} className="text-accent hover:underline">
                            {p.firstName} {p.lastName}
                          </Link>
                          <div className="text-xs text-text-muted mt-0.5">{p.position}</div>
                        </td>
                        <td className="py-2 px-2 text-right">{age(p.birthDate)}</td>
                        <td className="py-2 px-2 text-right font-bold text-accent">{overallScore(p).toFixed(1)}</td>
                        <td className="py-2 px-2 text-right font-bold text-success">+{(p.developmentVelocity ?? 0).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-10">
                <EmptyState
                  title="Oyuncu bulunamadı"
                  description="Arama kriterlerinize uygun oyuncu kaydı bulunamadı. Lütfen filtreleri kontrol edin."
                  icon="🔍"
                  action={
                    <button
                      onClick={() => {
                        setSearchQ("");
                        setSelectedPosition("");
                        setSelectedTags([]);
                        setMinTactical(0);
                        setMinPhysical(0);
                      }}
                      className="px-4 py-2 bg-white/5 border border-white/10 text-white rounded-xl text-sm font-semibold hover:bg-white/10 transition-all"
                    >
                      Filtreleri Temizle
                    </button>
                  }
                />
              </div>
            )}
          </div>
        </div>

        {/* ── Right: Charts & Gems ── */}
        <div className="lg:col-span-2 space-y-4">
          {/* ── Scatter Plot ── */}
          {scatterData.length > 0 && (
            <div className="rounded-2xl pv-card p-4">
              <div className="text-xs font-semibold text-white mb-3">Mevcut Skor vs Gelişim İvmesi</div>
              <ResponsiveContainer width="100%" height={280}>
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis type="number" dataKey="x" name="Skor" stroke="rgba(255,255,255,0.3)" label={{ value: "Skor", position: "insideBottomRight", offset: -5, fill: "rgba(255,255,255,0.5)", fontSize: 11 }} />
                  <YAxis type="number" dataKey="y" name="İvme" stroke="rgba(255,255,255,0.3)" />
                  <Tooltip contentStyle={{ background: "rgba(15,23,42,0.95)", border: "1px solid rgba(255,255,255,0.1)" }} />
                  <Scatter name="Oyuncular" data={scatterData} fill="#34d399" fillOpacity={0.7} />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* ── Radar Chart ── */}
          {radarData.length > 0 && (
            <div className="rounded-2xl pv-card p-4">
              <div className="text-xs font-semibold text-white mb-3">Seçili Oyuncu Karşılaştırması (Max 3)</div>
              <ResponsiveContainer width="100%" height={280}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(255,255,255,0.1)" />
                  <PolarAngleAxis dataKey="player" stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.6)", fontSize: 11 }} />
                  <PolarRadiusAxis stroke="rgba(255,255,255,0.2)" />
                  <Radar name="Teknik" dataKey="technical" stroke="#34d399" fill="#34d399" fillOpacity={0.15} />
                  <Radar name="Taktik" dataKey="tactical" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.15} />
                  <Tooltip contentStyle={{ background: "rgba(15,23,42,0.95)", border: "1px solid rgba(255,255,255,0.1)" }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* ── Hidden Gems ── */}
          <div className="rounded-2xl pv-card p-4">
            <div className="text-xs font-semibold text-white mb-3">Gizli Cevherler ({hiddenGems.length})</div>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {hiddenGems.slice(0, 10).map((p) => (
                <Link
                  key={p.id}
                  href={`/players/${p.id}`}
                  className="flex items-center justify-between p-2.5 rounded-lg bg-white/5 border border-white/10 hover:bg-accent/10 hover:border-accent/30 transition-all cursor-pointer"
                >
                  <div>
                    <div className="text-xs font-medium text-white">
                      {p.firstName} {p.lastName}
                    </div>
                    <div className="text-xs text-text-muted">{p.position} • {age(p.birthDate)} yaş</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-bold text-success">+{(p.developmentVelocity ?? 0).toFixed(2)}</div>
                    <div className="text-xs text-accent">{overallScore(p).toFixed(1)}/10</div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Scout Notes ── */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="text-sm font-semibold text-white">Son Scout Notları</div>
          <button onClick={() => setAddingNote(!addingNote)} className="px-3 py-1.5 rounded-lg text-xs font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all">
            {addingNote ? "İptal" : "+ Not Ekle"}
          </button>
        </div>

        {addingNote && (
          <div className="rounded-2xl pv-card p-5 space-y-3">
            <textarea value={noteText} onChange={(e) => setNoteText(e.target.value)} rows={3} placeholder="Scout notunuzu yazın..." className="w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm text-white placeholder:text-text-muted outline-none focus:ring-2 focus:ring-accent/40 resize-none" />
            <div className="flex items-center gap-3">
              <label className="text-xs text-text-muted">Puan:</label>
              <input type="range" min={1} max={10} step={0.1} value={noteRating} onChange={(e) => setNoteRating(Number(e.target.value))} className="flex-1" />
              <span className="text-sm font-bold text-accent w-8">{noteRating.toFixed(1)}</span>
            </div>
            <button disabled={!noteText.trim()} className="px-4 py-2 rounded-lg text-sm font-medium bg-success/20 border border-success/40 text-success hover:bg-success/30 transition-all disabled:opacity-40">
              Kaydet
            </button>
          </div>
        )}

        <div className="grid gap-4 lg:grid-cols-2">
          {notes.length ? (
            notes.map((n) => <ScoutNoteCard key={n.id} note={n as any} />)
          ) : (
            <div className="text-sm text-text-muted">Scout notu yok.</div>
          )}
        </div>
      </div>

      {/* ── Disclaimer ── */}
      <div className="rounded-xl bg-blue-500/5 border border-blue-500/20 p-4 text-sm text-blue-300/80">
        ℹ️ Scout veriler öneriler için tasarlanmıştır. Genç oyuncuların gelişimi zaman alabilir.{' '}
        <span className="italic">&ldquo;Daha fazla maç verisi gerekli&rdquo;</span> durumunda değerlendirmeyi ertele.
      </div>
    </div>
  );
}

