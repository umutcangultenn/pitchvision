"use client";

import React, { useMemo, useRef } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  mockMatches, mockAlerts, mockClips, mockPlayers,
  mockPerformances,
} from "@/data/demo";
import { EmptyState } from "@/components/ui/EmptyState";

// ── helpers ────────────────────────────────────────────────────────────────────
function fmtTime(s: number) {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
}

function severityColor(sev: string) {
  return {
    critical: "text-red-400 bg-red-400/10 border-red-400/30",
    high: "text-orange-400 bg-orange-400/10 border-orange-400/30",
    medium: "text-yellow-400 bg-yellow-400/10 border-yellow-400/30",
    low: "text-green-400 bg-green-400/10 border-green-400/30",
  }[sev] ?? "text-slate-400 bg-slate-400/10 border-slate-400/30";
}

function severityDot(sev: string) {
  return {
    critical: "bg-red-400",
    high: "bg-orange-400",
    medium: "bg-yellow-400",
    low: "bg-green-400",
  }[sev] ?? "bg-slate-400";
}

// ── drill mapping (mirrors backend) ───────────────────────────────────────────
const DRILL_MAP: Record<string, { title: string; duration: number; focus: string[] }> = {
  transition:          { title: "5 Saniye Karşı Pres Oyunu",          duration: 15, focus: ["counter_press", "transition_speed"] },
  defensive_line_break:{ title: "Savunma Çizgisi Senkronizasyonu",    duration: 18, focus: ["defensive_line", "communication"] },
  block_gap_wide:      { title: "8v8 Kompakt Blok Oyunu",             duration: 20, focus: ["compactness", "block_distance"] },
  depth_run_opportunity:{ title: "Üçüncü Adam Koşusu",               duration: 20, focus: ["timing", "through_balls"] },
  compactness_lost:    { title: "Destek Açısı ve Pas Opsiyonu Oyunu", duration: 22, focus: ["support_runs", "passing_options"] },
  pressing:            { title: "3 Saniye Pres Sprinti",              duration: 15, focus: ["pressing", "recovery"] },
  duel:                { title: "Duel + İkinci Top",                  duration: 18, focus: ["duel", "second_ball"] },
  wing_overload:       { title: "Kanat Bindirme Organizasyonu",       duration: 20, focus: ["overlapping", "crossing"] },
};

function getDrill(alertType: string) {
  return DRILL_MAP[alertType] ?? null;
}

// ── sub-components ─────────────────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-8">
      <h2 className="text-base font-semibold text-white border-b border-white/10 pb-2 mb-4">
        {title}
      </h2>
      {children}
    </section>
  );
}

function MetricBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-white/5 border border-white/10 p-4 text-center">
      <div className="text-2xl font-bold text-accent">{value}</div>
      <div className="text-xs text-text-muted mt-1">{label}</div>
    </div>
  );
}

function AlertRow({ alert }: { alert: typeof mockAlerts[0] }) {
  const drill = getDrill(alert.alertType);
  const clip = mockClips.find(c => c.id === alert.suggestedClipId);

  return (
    <div className={`rounded-xl border p-4 mb-3 ${severityColor(alert.severity)}`}>
      <div className="flex items-start gap-3">
        <span className={`mt-1 w-2.5 h-2.5 rounded-full flex-shrink-0 ${severityDot(alert.severity)}`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium text-sm text-white">{alert.title}</span>
            <span className="text-xs opacity-70">{fmtTime(alert.startTime)}</span>
            <span className="text-xs opacity-70">%{Math.round((alert.confidence ?? 0) * 100)} güven</span>
            <span className={`text-xs px-2 py-0.5 rounded-full border ${severityColor(alert.severity)}`}>
              {alert.severity}
            </span>
          </div>
          <p className="text-xs mt-1 opacity-80">{alert.description}</p>

          <div className="flex flex-wrap gap-2 mt-2">
            {clip && (
              <span className="text-xs bg-white/10 px-2 py-1 rounded-lg">
                ✂️ Klip: {clip.title}
              </span>
            )}
            {drill && (
              <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded-lg border border-blue-500/30">
                🏋️ {drill.title} ({drill.duration} dk)
              </span>
            )}
          </div>
        </div>
      </div>
      <p className="text-xs mt-3 opacity-60 italic">
        Bu uyarı otomatik analiz adayıdır. Nihai değerlendirme antrenör gözlemiyle birlikte yapılmalıdır.
      </p>
    </div>
  );
}

function DrillCard({ alertType, alertTitle }: { alertType: string; alertTitle: string }) {
  const drill = getDrill(alertType);
  if (!drill) return null;
  return (
    <div className="rounded-xl bg-blue-500/5 border border-blue-500/20 p-4 mb-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="font-medium text-sm text-white">{drill.title}</div>
          <div className="text-xs text-blue-400 mt-0.5">Tetikleyen: {alertTitle}</div>
        </div>
        <span className="text-xs bg-white/10 px-2 py-1 rounded-lg whitespace-nowrap">{drill.duration} dk</span>
      </div>
      <div className="flex flex-wrap gap-1 mt-2">
        {drill.focus.map(f => (
          <span key={f} className="text-xs bg-white/5 border border-white/10 px-2 py-0.5 rounded-full">{f}</span>
        ))}
      </div>
    </div>
  );
}

// ── main page ──────────────────────────────────────────────────────────────────

export default function MatchReportPage() {
  const params = useParams();
  const idParam = String(params.id);
  const matchId = Number(idParam);
  const isDemo = idParam === "demo-match" || !Number.isFinite(matchId);
  const printRef = useRef<HTMLDivElement>(null);

  const match = useMemo(
    () => (isDemo ? mockMatches[0] : mockMatches.find(m => m.id === matchId) ?? mockMatches[0]),
    [matchId, isDemo]
  );

  const alerts = useMemo(
    () => mockAlerts.filter(a => isDemo || a.matchId === matchId)
      .sort((a, b) => {
        const order: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 };
        return (order[a.severity] ?? 9) - (order[b.severity] ?? 9);
      }),
    [matchId, isDemo]
  );

  const clips = useMemo(
    () => mockClips.filter(c => isDemo || c.matchId === matchId),
    [matchId, isDemo]
  );

  const performances = useMemo(
    () => mockPerformances.filter(p => isDemo || p.matchId === matchId),
    [matchId, isDemo]
  );

  const players = useMemo(
    () => mockPlayers.filter(p => isDemo || performances.some(perf => perf.playerId === p.id)),
    [performances, isDemo]
  );

  // Deduplicated drills
  const drills = useMemo(() => {
    const seen = new Set<string>();
    return alerts
      .filter(a => {
        if (seen.has(a.alertType)) return false;
        seen.add(a.alertType);
        return getDrill(a.alertType) !== null;
      });
  }, [alerts]);

  // Top 3 findings
  const topFindings = useMemo(() => {
    const findings: string[] = [];
    if (alerts[0]) {
      findings.push(`En kritik uyarı: "${alerts[0].title}" (%${Math.round((alerts[0].confidence ?? 0) * 100)} güven, ${alerts[0].severity} önem)`);
    }
    findings.push("Takım kompaktlığı 18.4m ile iyi seviyede — blok mesafeleri korunmalı.");
    const best = players.reduce<typeof players[0] | null>((acc, p) => {
      const perf = performances.find(x => x.playerId === p.id);
      const avg = ((perf?.tacticalScore ?? 0) + (perf?.technicalScore ?? 0)) / 2;
      const accPerf = acc ? performances.find(x => x.playerId === acc.id) : null;
      const accAvg = accPerf ? ((accPerf.tacticalScore ?? 0) + (accPerf.technicalScore ?? 0)) / 2 : 0;
      return avg > accAvg ? p : acc;
    }, null);
    if (best) {
      const perf = performances.find(x => x.playerId === best.id);
      const avg = (((perf?.tacticalScore ?? 0) + (perf?.technicalScore ?? 0)) / 2).toFixed(1);
      findings.push(`En yüksek taktik+teknik ortalama: ${best.firstName} ${best.lastName} (${avg}/10)`);
    }
    return findings.slice(0, 3);
  }, [alerts, players, performances]);

  // Next match indicators
  const alertTypes = new Set(alerts.map(a => a.alertType));
  const indicators: string[] = [];
  if (alertTypes.has("defensive_line_break")) indicators.push("Savunma hattı düzgünlüğü — hat sapması < 4m hedefi");
  if (alertTypes.has("block_gap_wide") || alertTypes.has("transition")) indicators.push("Bloklar arası mesafe — savunma-orta saha < 25m hedefi");
  if (alertTypes.has("transition") || alertTypes.has("pressing")) indicators.push("Geçiş hızı — top kazanımından 5 saniyede ileri bölge");
  if (alertTypes.has("depth_run_opportunity")) indicators.push("Derin koşu zamanlaması — ofsayt sayısını azalt");
  indicators.push("Geçiş hızı hedefi: ≥ 5.1 m/s");
  indicators.push("Savunma-orta saha mesafesi: < 20m");

  const matchLabel = `${match.opponentName} — ${new Date(match.matchDate).toLocaleDateString("tr-TR")}`;
  const score = `${match.scoreFor}-${match.scoreAgainst}`;

  const handlePrint = () => window.print();

  return (
    <div className="space-y-6">
      {/* ── Header ── */}
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
        <div>
          <div className="text-sm text-text-muted">Maç Raporu</div>
          <h1 className="mt-1 text-2xl font-semibold text-white">{matchLabel}</h1>
        </div>
        <div className="flex gap-2 flex-wrap">
          <Link
            href={`/matches/${idParam}/analysis`}
            className="px-4 py-2 rounded-lg text-sm font-medium bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all"
          >
            ← Video Analizi
          </Link>
          <button
            onClick={handlePrint}
            className="px-4 py-2 rounded-lg text-sm font-medium bg-warning/20 border border-warning/40 text-warning hover:bg-warning/30 transition-all"
          >
            📥 PDF İndir
          </button>
          <button className="px-4 py-2 rounded-lg text-sm font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all">
            🔗 Paylaş
          </button>
          <Link
            href="/drills"
            className="inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium bg-success/20 border border-success/40 text-success hover:bg-success/30 transition-all"
          >
            Antrenman planına ekle
          </Link>
        </div>
      </div>

      {/* ── Report body ── */}
      <div ref={printRef} className="space-y-6 print:text-black">

        {/* 1. Kapak */}
        <div className="rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-white/10 p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="text-xs text-text-muted uppercase tracking-wider mb-1">Maç Analiz Raporu</div>
              <div className="text-xl font-bold text-white">
                U15 Kırmızı Takım vs {match.opponentName}
              </div>
              <div className="flex flex-wrap gap-3 mt-2 text-xs text-text-muted">
                <span>📅 {new Date(match.matchDate).toLocaleDateString("tr-TR")}</span>
                <span>🏷️ {match.ageCategory}</span>
                <span>📹 {match.videoSource}</span>
                <span>🎯 Kalibrasyon: İyi (0.8m)</span>
                <span>📊 Tracking: %94</span>
              </div>
            </div>
            <div className="text-5xl font-black text-accent">{score}</div>
          </div>
        </div>

        {/* 2. Maç Özeti */}
        <Section title="Maç Özeti">
          <p className="text-sm text-text-muted leading-relaxed">
            U15 Kırmızı Takım - {match.opponentName} maçı {score} {match.scoreFor > match.scoreAgainst ? "galibiyet" : match.scoreFor === match.scoreAgainst ? "beraberlik" : "mağlubiyet"} ile sonuçlandı.
            Analiz {alerts.length} taktiksel uyarı tespit etti; bunların {alerts.filter(a => ["high","critical"].includes(a.severity)).length} tanesi yüksek/kritik önem taşıyor.
            Takım şekli metrikleri ortalama 18.4m kompaktlık gösterdi.
          </p>
        </Section>

        {/* 3. En Önemli 3 Bulgu */}
        <Section title="En Önemli Bulgular">
          <ul className="space-y-2">
            {topFindings.map((f, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-text-muted">
                <span className="text-accent font-bold mt-0.5">{i + 1}.</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
        </Section>

        {/* 4. Takım Şekli Metrikleri */}
        <Section title="Takım Şekli Metrikleri">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <MetricBox label="Takım Boyu" value="47.2m" />
            <MetricBox label="Takım Genişliği" value="42.8m" />
            <MetricBox label="Kompaktlık" value="18.4m" />
            <MetricBox label="Sav-Orta Mesafe" value="21.4m" />
            <MetricBox label="Orta-Forvet Mesafe" value="16.8m" />
            <MetricBox label="Geçiş Hızı" value="4.6 m/s" />
          </div>
        </Section>

        {/* 5. Taktiksel Uyarılar */}
        <Section title={`Taktiksel Uyarılar (${alerts.length} adet)`}>
          {alerts.length === 0 ? (
            <p className="text-sm text-text-muted">Uyarı bulunamadı.</p>
          ) : (
            alerts.map(a => <AlertRow key={a.id} alert={a} />)
          )}
        </Section>

        {/* 6. Klipler */}
        <Section title={`Klipler (${clips.length} adet)`}>
          {clips.length === 0 ? (
            <p className="text-sm text-text-muted">Klip bulunamadı.</p>
          ) : (
            <div className="rounded-xl border border-white/10 overflow-hidden">
              {clips.map((c, i) => (
                <div key={c.id} className={`flex items-center gap-3 px-4 py-3 text-sm ${i < clips.length - 1 ? "border-b border-white/5" : ""}`}>
                  <span className="text-text-muted w-16 flex-shrink-0">{fmtTime(c.startTime)}</span>
                  <span className="flex-1 text-white font-medium">{c.title}</span>
                  <span className="text-xs text-text-muted">{c.description}</span>
                  <span className="text-xs bg-white/10 px-2 py-0.5 rounded-full">{c.tag}</span>
                  <div className="flex gap-1">
                    <button className="text-xs text-accent hover:underline">İndir</button>
                    <span className="text-text-muted">·</span>
                    <button className="text-xs text-accent hover:underline">Paylaş</button>
                    <span className="text-text-muted">·</span>
                    <button className="text-xs text-success hover:underline">Rapora Ekle</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Section>

        {/* 7. Oyuncu Performansı */}
        <Section title="Oyuncu Performansı">
          <div className="rounded-xl border border-white/10 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-xs text-text-muted">
                  <th className="text-left px-4 py-3">Oyuncu</th>
                  <th className="text-left px-4 py-3">Pos.</th>
                  <th className="text-right px-4 py-3">Süre</th>
                  <th className="text-right px-4 py-3">Taktik</th>
                  <th className="text-right px-4 py-3">Teknik</th>
                  <th className="text-right px-4 py-3">Fizik</th>
                  <th className="text-right px-4 py-3">Karar</th>
                  <th className="text-right px-4 py-3">Ort.</th>
                  <th className="text-right px-4 py-3">Uyarı</th>
                </tr>
              </thead>
              <tbody>
                {players.map(p => {
                  const perf = performances.find(x => x.playerId === p.id);
                  const avg = perf
                    ? (((perf.tacticalScore ?? 0) + (perf.technicalScore ?? 0) + (perf.physicalScore ?? 0) + (perf.decisionScore ?? 0)) / 4).toFixed(1)
                    : "—";
                  return (
                    <tr key={p.id} className="border-b border-white/5 hover:bg-white/3 transition-colors">
                      <td className="px-4 py-3 font-medium text-white">{p.firstName} {p.lastName}</td>
                      <td className="px-4 py-3 text-text-muted">{p.position}</td>
                      <td className="px-4 py-3 text-right text-text-muted">{perf?.minutesPlayed ?? 0}&apos;</td>
                      <td className="px-4 py-3 text-right">{perf?.tacticalScore?.toFixed(1) ?? "—"}</td>
                      <td className="px-4 py-3 text-right">{perf?.technicalScore?.toFixed(1) ?? "—"}</td>
                      <td className="px-4 py-3 text-right">{perf?.physicalScore?.toFixed(1) ?? "—"}</td>
                      <td className="px-4 py-3 text-right">{perf?.decisionScore?.toFixed(1) ?? "—"}</td>
                      <td className="px-4 py-3 text-right font-bold text-accent">{avg}</td>
                      <td className="px-4 py-3 text-right text-text-muted">{perf?.alertsInvolved ?? 0}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {/* Development notes */}
          {performances.filter(p => p.developmentNotes).map(perf => {
            const pl = players.find(p => p.id === perf.playerId);
            if (!pl) return null;
            return (
              <div key={perf.id} className="mt-2 text-xs text-text-muted bg-white/3 rounded-lg px-4 py-2">
                <span className="text-white font-medium">{pl.firstName} {pl.lastName}:</span> {perf.developmentNotes}
              </div>
            );
          })}
        </Section>

        {/* 8. Antrenman Önerileri */}
        <Section title="Antrenman Önerileri">
          {drills.length === 0 ? (
            <p className="text-sm text-text-muted">Öneri bulunamadı.</p>
          ) : (
            drills.map(a => <DrillCard key={a.id} alertType={a.alertType} alertTitle={a.title} />)
          )}
        </Section>

        {/* 9. Bir Sonraki Maçta Takip Edilecek Göstergeler */}
        <Section title="Bir Sonraki Maçta Takip Edilecek Göstergeler">
          <ul className="space-y-2">
            {indicators.slice(0, 5).map((ind, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-text-muted">
                <span className="text-warning mt-0.5">→</span>
                <span>{ind}</span>
              </li>
            ))}
          </ul>
        </Section>

        {/* Etik Not */}
        <div className="rounded-xl bg-yellow-500/5 border border-yellow-500/20 p-4 text-sm text-yellow-300/80">
          ⚠️ Bu rapor otomatik analiz adayları içerir. Nihai değerlendirme antrenör gözlemiyle birlikte yapılmalıdır.
        </div>

      </div>
    </div>
  );
}
