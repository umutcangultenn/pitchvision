"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";

import { useAppStore } from "@/lib/appStore";
import { useMatches } from "@/hooks/useMatches";
import { mockTeams } from "@/data/demo";
import type { Match } from "@/types/domain";

import { FilterBar } from "@/components/ui/FilterBar";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { MatchListCard, type MatchUiStatus } from "@/components/cards/MatchListCard";
import { mockAlerts, mockVideos } from "@/data/demo";

export default function MatchesPage() {
  const { teamId } = useAppStore();
  const { data: allMatches, loading, error, refetch } = useMatches();
  const [teamFilter, setTeamFilter] = useState<number>(teamId);
  const [ageCategory, setAgeCategory] = useState<string>("all");
  const [status, setStatus] = useState<string>("all");
  const [videoSource, setVideoSource] = useState<string>("all");
  const [opponent, setOpponent] = useState<string>("");
  const [minAlerts, setMinAlerts] = useState<number>(0);
  const [fromDate, setFromDate] = useState<string>("");
  const [toDate, setToDate] = useState<string>("");

  const matches = useMemo(() => {
    const source = allMatches ?? [];
    const byTeam = source.filter((m) => m.teamId === teamFilter);

    const getAlertCount = (matchId: number) =>
      mockAlerts.filter((a) => a.matchId === matchId).length;

    return byTeam
      .filter((m) => (ageCategory === "all" ? true : m.ageCategory === ageCategory))
      .filter((m) => (videoSource === "all" ? true : m.videoSource === videoSource))
      .filter((m) => {
        if (!opponent.trim()) return true;
        return m.opponentName.toLowerCase().includes(opponent.toLowerCase());
      })
      .filter((m) => (minAlerts ? getAlertCount(m.id) >= minAlerts : true))
      .filter((m) => {
        if (!fromDate && !toDate) return true;
        const t = new Date(m.matchDate).getTime();
        const fromOk = fromDate ? t >= new Date(fromDate).getTime() : true;
        const toOk = toDate ? t <= new Date(toDate).getTime() : true;
        return fromOk && toOk;
      })
      .filter((m) => {
        if (status === "all") return true;
        // UI status mapping
        const ui =
          m.status === "completed"
            ? "Analiz tamamlandı"
            : m.status === "processing"
            ? "İşleniyor"
            : "Kalibrasyon bekliyor";
        return ui === status;
      })
      .sort((a, b) => new Date(b.matchDate).getTime() - new Date(a.matchDate).getTime());
  }, [teamFilter, ageCategory, status, videoSource, opponent, minAlerts, fromDate, toDate]);

  const teamName = useMemo(() => mockTeams.find((t) => t.id === teamFilter)?.name ?? "Takım", [teamFilter]);

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-10 rounded-xl bg-white/5 w-64" />
        {[...Array(3)].map((_, i) => <div key={i} className="h-24 rounded-2xl bg-white/5" />)}
      </div>
    );
  }

  if (error && !allMatches) {
    return (
      <ErrorState
        title="Maçlar yüklenemedi"
        description={error.message}
        icon="📡"
        action={<button onClick={refetch} className="px-4 py-2 text-sm font-semibold rounded-xl bg-emerald-600 text-white hover:bg-emerald-500 transition-all">Yeniden Dene</button>}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm font-medium text-emerald-200/80">Maçlar</div>
        <h1 className="mt-1 text-2xl font-semibold text-white">Maçlar</h1>
        <p className="mt-2 max-w-2xl text-sm text-text-muted">
          Filtreleyin, analizi açın, raporu görüntüleyin ve klipleri yönetin. (Mock demo)
        </p>
      </div>

      <FilterBar
        left={
          <div className="flex flex-col gap-3 md:flex-row md:flex-wrap md:items-center">
            <Link
              href="/matches/new"
              className="inline-flex h-10 items-center justify-center rounded-xl bg-emerald-600 px-4 text-sm font-semibold text-white hover:bg-emerald-500"
            >
              Yeni Maç Yükle
            </Link>

            <select
              value={teamFilter}
              onChange={(e) => setTeamFilter(Number(e.target.value))}
              className="h-10 rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
            >
              {mockTeams.map((t) => (
                <option key={t.id} value={t.id} className="bg-[#0a0f0d]">
                  {t.name}
                </option>
              ))}
            </select>

            <select
              value={ageCategory}
              onChange={(e) => setAgeCategory(e.target.value)}
              className="h-10 rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
            >
              <option value="all" className="bg-[#0a0f0d]">
                Yaş: Tümü
              </option>
              {Array.from(new Set(mockMatches.map((m) => m.ageCategory))).map((a) => (
                <option key={a} value={a} className="bg-[#0a0f0d]">
                  {a}
                </option>
              ))}
            </select>

            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="h-10 rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
            >
              <option value="all" className="bg-[#0a0f0d]">
                Durum: Tümü
              </option>
              <option value="Analiz tamamlandı" className="bg-[#0a0f0d]">Analiz tamamlandı</option>
              <option value="Kalibrasyon bekliyor" className="bg-[#0a0f0d]">Kalibrasyon bekliyor</option>
              <option value="İşleniyor" className="bg-[#0a0f0d]">İşleniyor</option>
              <option value="Hata" className="bg-[#0a0f0d]">Hata</option>
            </select>

            <select
              value={videoSource}
              onChange={(e) => setVideoSource(e.target.value)}
              className="h-10 rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
            >
              <option value="all" className="bg-[#0a0f0d]">
                Video kaynağı: Tümü
              </option>
              <option value="file_upload" className="bg-[#0a0f0d]">Dosya</option>
              <option value="url_stream" className="bg-[#0a0f0d]">URL</option>
              <option value="youtube" className="bg-[#0a0f0d]">YouTube</option>
              <option value="other" className="bg-[#0a0f0d]">Diğer</option>
            </select>

            <input
              value={opponent}
              onChange={(e) => setOpponent(e.target.value)}
              className="h-10 w-64 max-w-full rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              placeholder="Rakip..."
            />

            <input
              value={String(minAlerts || "")}
              onChange={(e) => setMinAlerts(Number(e.target.value || 0))}
              className="h-10 w-40 rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              placeholder="Alert ≥"
              inputMode="numeric"
            />

            <input
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="h-10 rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              type="date"
              aria-label="Başlangıç tarihi"
            />
            <input
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="h-10 rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              type="date"
              aria-label="Bitiş tarihi"
            />
          </div>
        }
        right={<div className="text-sm text-text-muted">Toplam: {matches.length}</div>}
      />

      {matches.length ? (
        <div className="space-y-4">
          {matches.map((m) => {
            const alertCount = mockAlerts.filter((a) => a.matchId === m.id).length;
            const video = mockVideos.find((v) => v.matchId === m.id);

            // Demo UI status
            const uiStatus: MatchUiStatus =
              m.status === "completed"
                ? "Analiz tamamlandı"
                : m.status === "processing"
                ? "İşleniyor"
                : "Kalibrasyon bekliyor";

            // Placeholder advanced stats (sonra gerçek metriklerden gelecek)
            const teamLengthM = m.id === 1001 ? 34.2 : 36.8;
            const compactnessM = m.id === 1001 ? 18.4 : 20.1;

            return (
              <MatchListCard
                key={m.id}
                match={m as Match}
                teamName={teamName}
                video={video as any}
                uiStatus={uiStatus}
                teamLengthM={teamLengthM}
                compactnessM={compactnessM}
                alertCount={alertCount}
              />
            );
          })}
        </div>
      ) : (
        <EmptyState
          title="Maç bulunamadı"
          description="Seçili filtre kriterlerine uygun maç bulunamadı. Lütfen filtreleri temizleyin veya yeni bir maç yükleyin."
          icon="⚽"
          action={
            <Link
              href="/matches/new"
              className="inline-flex rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500 transition-all shadow-lg shadow-emerald-900/20"
            >
              Yeni Maç Yükle
            </Link>
          }
          secondaryAction={
            <button
              onClick={() => {
                setAgeCategory("all");
                setStatus("all");
                setVideoSource("all");
                setOpponent("");
                setMinAlerts(0);
                setFromDate("");
                setToDate("");
              }}
              className="px-4 py-2 text-sm font-semibold rounded-xl bg-white/5 border border-white/10 text-text-soft hover:text-white transition-all"
            >
              Filtreleri Temizle
            </button>
          }
        />
      )}
    </div>
  );
}

