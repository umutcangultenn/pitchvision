"use client";

import React, { useMemo, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  mockPlayers, mockPerformances, mockClips,
  mockScoutingNotes, mockMatches,
} from "@/data/demo";
import { RadarChartCard } from "@/components/charts/RadarChartCard";
import { TrendChartCard } from "@/components/charts/TrendChartCard";
import { ErrorState } from "@/components/ui/ErrorState";
import type { Player } from "@/types/domain";

// ── types ──────────────────────────────────────────────────────────────────────
type Tab = "overview" | "performances" | "trends" | "tactical" | "scouting" | "clips";

// ── helpers ────────────────────────────────────────────────────────────────────
function age(birthDate: string) {
  const bd = new Date(birthDate);
  const today = new Date();
  let a = today.getFullYear() - bd.getFullYear();
  if (today.getMonth() < bd.getMonth() || (today.getMonth() === bd.getMonth() && today.getDate() < bd.getDate())) a--;
  return a;
}

function overall(p: Player) {
  const scores = [p.technicalScore ?? 0, p.tacticalScore ?? 0, p.physicalScore ?? 0, p.decisionScore ?? 0];
  return (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1);
}

function fmtTime(s: number) {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
}

function ScoreBadge({ value, max = 10 }: { value: number; max?: number }) {
  const pct = (value / max) * 100;
  const color = pct >= 75 ? "text-success" : pct >= 55 ? "text-accent" : pct >= 40 ? "text-warning" : "text-red-400";
  return <span className={`font-bold ${color}`}>{value.toFixed(1)}</span>;
}

function MetricRow({ label, value, max = 10 }: { label: string; value: number; max?: number }) {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-text-muted">{label}</span>
        <ScoreBadge value={value} max={max} />
      </div>
      <div className="h-1.5 rounded-full bg-white/10">
        <div className="h-full rounded-full bg-accent transition-all" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

// ── Tactical profile data ──────────────────────────────────────────────────────
function getTacticalProfile(position: string, p: Player) {
  const pos = position.toUpperCase();
  if (["CB", "LB", "RB", "SW"].includes(pos)) {
    return {
      group: "Stoper / Bek",
      metrics: [
        { label: "Hat Uyumu",              value: +(((p.tacticalScore ?? 5) * 0.95).toFixed(1)) },
        { label: "Savunma Arkası Kontrol", value: +(((p.tacticalScore ?? 5) * 0.90).toFixed(1)) },
        { label: "Topla Çıkış",            value: +(((p.technicalScore ?? 5) * 0.85).toFixed(1)) },
        { label: "Baskı Altında Pas",      value: +(((p.decisionScore ?? 5) * 0.88).toFixed(1)) },
      ],
    };
  }
  if (["CM", "CDM", "CAM", "DM"].includes(pos)) {
    return {
      group: "Merkez Orta Saha",
      metrics: [
        { label: "Pas Bağlantısı",         value: +(((p.technicalScore ?? 5) * 0.92).toFixed(1)) },
        { label: "Destek Açısı",           value: +(((p.tacticalScore ?? 5) * 0.88).toFixed(1)) },
        { label: "Geçiş Savunması",        value: +(((p.tacticalScore ?? 5) * 0.85).toFixed(1)) },
        { label: "Top Alma Konumu",        value: +(((p.decisionScore ?? 5) * 0.90).toFixed(1)) },
      ],
    };
  }
  if (["LW", "RW", "LM", "RM", "WF"].includes(pos)) {
    return {
      group: "Kanat",
      metrics: [
        { label: "Derin Koşu",             value: +(((p.physicalScore ?? 5) * 0.90).toFixed(1)) },
        { label: "Genişlik Koruma",        value: +(((p.tacticalScore ?? 5) * 0.85).toFixed(1)) },
        { label: "1v1 Katkı",              value: +(((p.technicalScore ?? 5) * 0.88).toFixed(1)) },
        { label: "Geri Dönüş Savunması",   value: +(((p.physicalScore ?? 5) * 0.82).toFixed(1)) },
      ],
    };
  }
  if (["ST", "CF", "SS"].includes(pos)) {
    return {
      group: "Forvet",
      metrics: [
        { label: "Bitiricilik",            value: +(((p.technicalScore ?? 5) * 0.92).toFixed(1)) },
        { label: "Hareket Kalitesi",       value: +(((p.physicalScore ?? 5) * 0.88).toFixed(1)) },
        { label: "Bağlantı Oyunu",         value: +(((p.decisionScore ?? 5) * 0.85).toFixed(1)) },
        { label: "Pres Katkısı",           value: +(((p.tacticalScore ?? 5) * 0.80).toFixed(1)) },
      ],
    };
  }
  return {
    group: "Genel",
    metrics: [
      { label: "Teknik",   value: p.technicalScore ?? 5 },
      { label: "Taktik",   value: p.tacticalScore ?? 5 },
      { label: "Fiziksel", value: p.physicalScore ?? 5 },
      { label: "Karar",    value: p.decisionScore ?? 5 },
    ],
  };
}

// ── 8-week trend (deterministic from scores) ───────────────────────────────────
function buildTrend(p: Player) {
  const weeks = ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"];
  const base = {
    technical: p.technicalScore ?? 5,
    tactical:  p.tacticalScore ?? 5,
    physical:  p.physicalScore ?? 5,
    decision:  p.decisionScore ?? 5,
  };
  return weeks.map((w, i) => {
    const d = (i - 3.5) * 0.04;
    return {
      x: w,
      technical: +Math.min(10, Math.max(1, base.technical + d)).toFixed(1),
      tactical:  +Math.min(10, Math.max(1, base.tactical  + d * 0.8)).toFixed(1),
      physical:  +Math.min(10, Math.max(1, base.physical  + d * 0.6)).toFixed(1),
      decision:  +Math.min(10, Math.max(1, base.decision  + d * 0.9)).toFixed(1),
    };
  });
}

// ── Main page ──────────────────────────────────────────────────────────────────
export default function PlayerPassportPage() {
  const params = useParams();
  const playerId = Number(params.id);
  const [tab, setTab] = useState<Tab>("overview");
  const [addingNote, setAddingNote] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [noteRating, setNoteRating] = useState(7.0);
  const [localNotes, setLocalNotes] = useState<typeof mockScoutingNotes>([]);

  const player = useMemo(() => mockPlayers.find(p => p.id === playerId) as Player | undefined, [playerId]);
  const performances = useMemo(() => mockPerformances.filter(x => x.playerId === playerId), [playerId]);
  const clips = useMemo(() => (mockClips as any[]).filter(c => c.playerId === playerId), [playerId]);
  const scoutNotes = useMemo(
    () => [...mockScoutingNotes.filter(n => n.playerId === playerId), ...localNotes],
    [playerId, localNotes]
  );

  if (!player) return <ErrorState title="Oyuncu bulunamadı" description="Lütfen oyuncu listesine dönün." />;

  const playerAge = age(player.birthDate);
  const overallScore = overall(player);
  const radarData = [
    { metric: "Teknik",        value: (player.technicalScore ?? 5) / 10 },
    { metric: "Taktik",        value: (player.tacticalScore ?? 5) / 10 },
    { metric: "Fiziksel",      value: (player.physicalScore ?? 5) / 10 },
    { metric: "Karar Verme",   value: (player.decisionScore ?? 5) / 10 },
    { metric: "Topsuz Oyun",   value: ((player.tacticalScore ?? 5) * 0.9) / 10 },
    { metric: "Geçiş Katkısı", value: ((player.physicalScore ?? 5) * 0.85) / 10 },
  ];
  const trend = buildTrend(player);
  const tacticalProfile = getTacticalProfile(player.position, player);

  const avgMaxSpeed = performances.length
    ? (performances.reduce((s, p) => s + (p.maxSpeed ?? 0), 0) / performances.length).toFixed(1)
    : "—";
  const avgSpeed = performances.length
    ? (performances.reduce((s, p) => s + (p.averageSpeed ?? 0), 0) / performances.length).toFixed(1)
    : "—";
  const totalPositive = performances.reduce((s, p) => s + (p.positiveActions ?? 0), 0);
  const totalAlerts = performances.reduce((s, p) => s + (p.alertsInvolved ?? 0), 0);

  const TABS: { key: Tab; label: string; icon: string }[] = [
    { key: "overview",      label: "Genel Bakış",       icon: "📊" },
    { key: "performances",  label: "Maç Performansları", icon: "⚽" },
    { key: "trends",        label: "Gelişim Trendleri",  icon: "📈" },
    { key: "tactical",      label: "Taktiksel Profil",   icon: "🎯" },
    { key: "scouting",      label: "Scouting Notları",   icon: "📝" },
    { key: "clips",         label: "Klipler",            icon: "✂️" },
  ];

  function handleAddNote() {
    if (!noteText.trim()) return;
    setLocalNotes(prev => [...prev, {
      id: Date.now(),
      playerId,
      scoutId: 99,
      note: noteText.trim(),
      rating: noteRating,
      tagsJson: [],
      createdAt: new Date().toISOString(),
    }]);
    setNoteText("");
    setNoteRating(7.0);
    setAddingNote(false);
  }

  return (
    <div className="space-y-6">

      {/* ── Profile header ── */}
      <div className="rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-white/10 p-6">
        <div className="flex flex-col md:flex-row md:items-start gap-6">
          {/* Avatar */}
          <div className="w-20 h-20 rounded-2xl bg-white/10 border border-white/20 flex items-center justify-center text-3xl flex-shrink-0">
            {player.firstName[0]}{player.lastName[0]}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-bold text-white">{player.firstName} {player.lastName}</h1>
              <span className="text-xs bg-accent/20 text-accent border border-accent/30 px-2 py-0.5 rounded-full">{player.position}</span>
            </div>
            <div className="flex flex-wrap gap-4 mt-2 text-sm text-text-muted">
              <span>🎂 {playerAge} yaş</span>
              <span>👟 {player.dominantFoot === "right" ? "Sağ ayak" : player.dominantFoot === "left" ? "Sol ayak" : player.dominantFoot}</span>
              {player.heightCm && <span>📏 {player.heightCm} cm</span>}
              {player.weightKg && <span>⚖️ {player.weightKg} kg</span>}
              <span>🏟️ U15 Kırmızı Takım</span>
            </div>
            <div className="flex flex-wrap gap-3 mt-3">
              <div className="rounded-xl bg-white/5 border border-white/10 px-4 py-2 text-center">
                <div className="text-xs text-text-muted">Genel Skor</div>
                <div className="text-xl font-bold text-accent">{overallScore}</div>
              </div>
              <div className="rounded-xl bg-white/5 border border-white/10 px-4 py-2 text-center">
                <div className="text-xs text-text-muted">Gelişim İvmesi</div>
                <div className="text-xl font-bold text-success">+{player.developmentVelocity?.toFixed(2)}</div>
              </div>
              <div className="rounded-xl bg-white/5 border border-white/10 px-4 py-2 text-center">
                <div className="text-xs text-text-muted">Maç Sayısı</div>
                <div className="text-xl font-bold text-white">{performances.length}</div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col gap-2">
            <button onClick={() => window.print()} className="px-4 py-2 rounded-lg text-sm font-medium bg-warning/20 border border-warning/40 text-warning hover:bg-warning/30 transition-all">
              📥 PDF Export
            </button>
            <button onClick={() => { setTab("scouting"); setAddingNote(true); }} className="px-4 py-2 rounded-lg text-sm font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all">
              📝 Scout Notu Ekle
            </button>
            <Link href="/players" className="px-4 py-2 rounded-lg text-sm font-medium bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all text-center">
              ← Oyuncular
            </Link>
          </div>
        </div>
      </div>

      {/* ── Tabs ── */}
      <div className="flex gap-1 flex-wrap">
        {TABS.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === t.key
                ? "bg-accent/20 border border-accent/40 text-accent"
                : "bg-white/5 border border-white/10 text-text-muted hover:bg-white/10"
            }`}
          >
            <span>{t.icon}</span>
            <span>{t.label}</span>
          </button>
        ))}
      </div>

      {/* ── Tab content ── */}
      {tab === "overview" && (
        <OverviewTab
          player={player}
          radarData={radarData}
          avgMaxSpeed={avgMaxSpeed}
          avgSpeed={avgSpeed}
          totalPositive={totalPositive}
          totalAlerts={totalAlerts}
          performances={performances}
        />
      )}
      {tab === "performances" && <PerformancesTab performances={performances} />}
      {tab === "trends" && <TrendsTab trend={trend} />}
      {tab === "tactical" && <TacticalTab profile={tacticalProfile} />}
      {tab === "scouting" && (
        <ScoutingTab
          notes={scoutNotes as any[]}
          adding={addingNote}
          noteText={noteText}
          noteRating={noteRating}
          onNoteChange={setNoteText}
          onRatingChange={setNoteRating}
          onAdd={handleAddNote}
          onToggleAdd={() => setAddingNote(v => !v)}
        />
      )}
      {tab === "clips" && <ClipsTab clips={clips} />}

      {/* Disclaimer */}
      <div className="rounded-xl bg-yellow-500/5 border border-yellow-500/20 p-4 text-sm text-yellow-300/80">
        ⚠️ Oyuncu gelişim skoru tek başına karar kriteri değildir. Maç verileri, antrenör gözlemi ve gelişim süreci birlikte değerlendirilmelidir.
      </div>

    </div>
  );
}

// ── Tab components ─────────────────────────────────────────────────────────────

function OverviewTab({ player, radarData, avgMaxSpeed, avgSpeed, totalPositive, totalAlerts, performances }: {
  player: Player;
  radarData: { metric: string; value: number }[];
  avgMaxSpeed: string;
  avgSpeed: string;
  totalPositive: number;
  totalAlerts: number;
  performances: typeof mockPerformances;
}) {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Radar */}
      <RadarChartCard title="Oyuncu Profili" data={radarData} />

      {/* Metrics */}
      <div className="rounded-2xl pv-card p-5 space-y-4">
        <div className="text-sm font-semibold text-white">Özet Metrikler</div>
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: "Maks Hız",          value: `${avgMaxSpeed} km/h` },
            { label: "Ort. Hız",          value: `${avgSpeed} km/h` },
            { label: "Pozitif Aksiyon",   value: String(totalPositive) },
            { label: "Taktiksel Uyarı",   value: String(totalAlerts) },
            { label: "Gelişim İvmesi",    value: `+${player.developmentVelocity?.toFixed(2)}` },
            { label: "Maç Sayısı",        value: String(performances.length) },
          ].map(m => (
            <div key={m.label} className="rounded-xl bg-white/5 border border-white/10 p-3">
              <div className="text-xs text-text-muted">{m.label}</div>
              <div className="text-base font-bold text-white mt-1">{m.value}</div>
            </div>
          ))}
        </div>

        <div className="pt-2 space-y-3">
          <div className="text-xs font-medium text-text-muted uppercase tracking-wider">Skor Dağılımı</div>
          <MetricRow label="Teknik"   value={player.technicalScore ?? 0} />
          <MetricRow label="Taktik"   value={player.tacticalScore ?? 0} />
          <MetricRow label="Fiziksel" value={player.physicalScore ?? 0} />
          <MetricRow label="Karar"    value={player.decisionScore ?? 0} />
        </div>
      </div>
    </div>
  );
}

function PerformancesTab({ performances }: { performances: typeof mockPerformances }) {
  if (!performances.length) {
    return <div className="text-sm text-text-muted">Performans kaydı bulunamadı.</div>;
  }
  return (
    <div className="space-y-4">
      {performances.map(perf => {
        const match = mockMatches.find(m => m.id === perf.matchId);
        const avg = (((perf.tacticalScore ?? 0) + (perf.technicalScore ?? 0) + (perf.physicalScore ?? 0) + (perf.decisionScore ?? 0)) / 4).toFixed(1);
        return (
          <div key={perf.id} className="rounded-2xl pv-card p-5">
            <div className="flex items-start justify-between gap-4 flex-wrap">
              <div>
                <div className="font-semibold text-white">
                  {match ? `vs ${match.opponentName}` : `Maç #${perf.matchId}`}
                </div>
                <div className="text-xs text-text-muted mt-0.5">
                  {match ? new Date(match.matchDate).toLocaleDateString("tr-TR") : ""}
                  {perf.minutesPlayed ? ` · ${perf.minutesPlayed}'` : ""}
                </div>
              </div>
              <div className="text-2xl font-black text-accent">{avg}</div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
              {[
                { label: "Teknik",   value: perf.technicalScore ?? 0 },
                { label: "Taktik",   value: perf.tacticalScore ?? 0 },
                { label: "Fiziksel", value: perf.physicalScore ?? 0 },
                { label: "Karar",    value: perf.decisionScore ?? 0 },
              ].map(s => (
                <div key={s.label} className="rounded-xl bg-white/5 border border-white/10 p-3 text-center">
                  <div className="text-xs text-text-muted">{s.label}</div>
                  <div className="text-lg font-bold text-white mt-1">{s.value.toFixed(1)}</div>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-3 gap-3 mt-3">
              <div className="rounded-xl bg-white/5 border border-white/10 p-3 text-center">
                <div className="text-xs text-text-muted">Maks Hız</div>
                <div className="text-sm font-bold text-white mt-1">{perf.maxSpeed ?? "—"} km/h</div>
              </div>
              <div className="rounded-xl bg-white/5 border border-white/10 p-3 text-center">
                <div className="text-xs text-text-muted">Pozitif Aksiyon</div>
                <div className="text-sm font-bold text-white mt-1">{perf.positiveActions ?? 0}</div>
              </div>
              <div className="rounded-xl bg-white/5 border border-white/10 p-3 text-center">
                <div className="text-xs text-text-muted">Uyarı</div>
                <div className="text-sm font-bold text-white mt-1">{perf.alertsInvolved ?? 0}</div>
              </div>
            </div>
            {perf.developmentNotes && (
              <p className="mt-3 text-xs text-text-muted bg-white/3 rounded-lg px-3 py-2">
                💬 {perf.developmentNotes}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}

function TrendsTab({ trend }: { trend: ReturnType<typeof buildTrend> }) {
  const lines = [
    { key: "technical" as const, label: "Teknik",   color: "#34d399" },
    { key: "tactical"  as const, label: "Taktik",   color: "#38bdf8" },
    { key: "physical"  as const, label: "Fiziksel", color: "#f97316" },
    { key: "decision"  as const, label: "Karar",    color: "#a78bfa" },
  ];
  return (
    <div className="space-y-4">
      <div className="rounded-2xl pv-card p-5">
        <div className="text-sm font-semibold text-white mb-4">8 Haftalık Gelişim Trendi</div>
        <div className="flex flex-wrap gap-3 mb-4">
          {lines.map(l => (
            <span key={l.key} className="flex items-center gap-1.5 text-xs text-text-muted">
              <span className="w-3 h-0.5 rounded-full inline-block" style={{ background: l.color }} />
              {l.label}
            </span>
          ))}
        </div>
        {/* Simple sparkline table */}
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-2 pr-4 text-text-muted font-normal">Hafta</th>
                {lines.map(l => (
                  <th key={l.key} className="text-right py-2 px-2 font-normal" style={{ color: l.color }}>{l.label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {trend.map(row => (
                <tr key={row.x} className="border-b border-white/5">
                  <td className="py-2 pr-4 text-text-muted">{row.x}</td>
                  {lines.map(l => (
                    <td key={l.key} className="py-2 px-2 text-right font-medium text-white">{row[l.key]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      {lines.map(l => (
        <TrendChartCard
          key={l.key}
          title={`${l.label} Trendi`}
          data={trend.map(r => ({ x: r.x, y: r[l.key] / 10 }))}
        />
      ))}
    </div>
  );
}

function TacticalTab({ profile }: { profile: ReturnType<typeof getTacticalProfile> }) {
  return (
    <div className="space-y-4">
      <div className="rounded-2xl pv-card p-5">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-sm font-semibold text-white">Taktiksel Profil</span>
          <span className="text-xs bg-accent/20 text-accent border border-accent/30 px-2 py-0.5 rounded-full">{profile.group}</span>
        </div>
        <div className="space-y-4">
          {profile.metrics.map(m => (
            <MetricRow key={m.label} label={m.label} value={m.value} />
          ))}
        </div>
      </div>
      <div className="rounded-xl bg-blue-500/5 border border-blue-500/20 p-4 text-sm text-blue-300/80">
        ℹ️ Taktiksel metrikler oyuncunun pozisyonuna göre hesaplanmaktadır. Farklı pozisyonlarda farklı kriterler ön plana çıkar.
      </div>
    </div>
  );
}

function ScoutingTab({ notes, adding, noteText, noteRating, onNoteChange, onRatingChange, onAdd, onToggleAdd }: {
  notes: any[];
  adding: boolean;
  noteText: string;
  noteRating: number;
  onNoteChange: (v: string) => void;
  onRatingChange: (v: number) => void;
  onAdd: () => void;
  onToggleAdd: () => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold text-white">Scouting Notları ({notes.length})</div>
        <button
          onClick={onToggleAdd}
          className="px-3 py-1.5 rounded-lg text-xs font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all"
        >
          {adding ? "İptal" : "+ Not Ekle"}
        </button>
      </div>

      {adding && (
        <div className="rounded-2xl pv-card p-5 space-y-3">
          <div className="text-sm font-medium text-white">Yeni Scout Notu</div>
          <textarea
            value={noteText}
            onChange={e => onNoteChange(e.target.value)}
            rows={3}
            placeholder="Gözlem notunuzu yazın..."
            className="w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm text-white placeholder:text-text-muted outline-none focus:ring-2 focus:ring-accent/40 resize-none"
          />
          <div className="flex items-center gap-3">
            <label className="text-xs text-text-muted">Puan:</label>
            <input
              type="range" min={1} max={10} step={0.1}
              value={noteRating}
              onChange={e => onRatingChange(Number(e.target.value))}
              className="flex-1"
            />
            <span className="text-sm font-bold text-accent w-8">{noteRating.toFixed(1)}</span>
          </div>
          <button
            onClick={onAdd}
            disabled={!noteText.trim()}
            className="px-4 py-2 rounded-lg text-sm font-medium bg-success/20 border border-success/40 text-success hover:bg-success/30 transition-all disabled:opacity-40"
          >
            Kaydet
          </button>
        </div>
      )}

      {notes.length === 0 && !adding && (
        <div className="text-sm text-text-muted">Henüz scouting notu yok.</div>
      )}

      {notes.map((n: any) => (
        <div key={n.id} className="rounded-2xl pv-card p-5">
          <div className="flex items-start justify-between gap-3">
            <p className="text-sm text-text-muted flex-1">{n.note}</p>
            <div className="text-xl font-black text-accent flex-shrink-0">{(n.rating ?? 0).toFixed(1)}</div>
          </div>
          <div className="flex flex-wrap gap-2 mt-3">
            {(n.tagsJson ?? []).map((tag: string) => (
              <span key={tag} className="text-xs bg-white/5 border border-white/10 px-2 py-0.5 rounded-full">{tag}</span>
            ))}
          </div>
          <div className="text-xs text-text-muted mt-2">
            {n.createdAt ? new Date(n.createdAt).toLocaleDateString("tr-TR") : ""}
          </div>
        </div>
      ))}
    </div>
  );
}

function ClipsTab({ clips }: { clips: any[] }) {
  if (!clips.length) {
    return <div className="text-sm text-text-muted">Bu oyuncuya ait klip bulunamadı.</div>;
  }
  return (
    <div className="space-y-3">
      {clips.map((c: any) => (
        <div key={c.id} className="rounded-2xl pv-card p-5">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="font-medium text-white text-sm">{c.title}</div>
              <div className="text-xs text-text-muted mt-1">{c.description}</div>
              <div className="flex gap-2 mt-2">
                <span className="text-xs text-text-muted">{fmtTime(c.startTime)} – {fmtTime(c.endTime)}</span>
                <span className="text-xs bg-white/10 px-2 py-0.5 rounded-full">{c.tag}</span>
              </div>
            </div>
            <div className="flex flex-col gap-1">
              <button className="text-xs text-accent hover:underline">▶ Oynat</button>
              <button className="text-xs text-text-muted hover:underline">İndir</button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
