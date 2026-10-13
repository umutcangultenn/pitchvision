"use client";

import React, { useMemo, useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { mockAlerts, mockMatches } from "@/data/demo";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { TacticalMetricCard } from "@/components/cards/TacticalMetricCard";
import { VideoPlayer } from "@/components/media/VideoPlayer";
import { AlertCard } from "@/components/cards/AlertCard";
import { Timeline, type TimelineItem } from "@/components/ui/Timeline";
import { apiGetMatchById, apiGetAnalysis, apiGetAlerts, apiGetScoutingPlayers, apiGetMatchVideo } from "@/lib/api";

import type { Match, TacticalAlert, Player, VideoAsset } from "@/types/domain";

const subTabs = [
  { key: "processing", label: "İşleme", href: (id: string) => `/matches/${id}/processing` },
  { key: "calibration", label: "Kalibrasyon", href: (id: string) => `/matches/${id}/calibration` },
  { key: "analysis", label: "Analiz", href: (id: string) => `/matches/${id}/analysis` },
  { key: "report", label: "Rapor", href: (id: string) => `/matches/${id}/report` },
];

export default function MatchDetailPage() {
  const params = useParams();
  const idParam = String(params.id);
  const matchId = Number(idParam);

  const [match, setMatch] = useState<Match | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [alerts, setAlerts] = useState<TacticalAlert[]>([]);
  const [players, setPlayers] = useState<Player[]>([]);
  const [video, setVideo] = useState<VideoAsset | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch match
        const matchRes = await apiGetMatchById(matchId);
        if (matchRes.ok) {
          setMatch(matchRes.data);
        } else {
          const fallback = mockMatches.find((m) => m.id === matchId);
          setMatch(fallback as Match);
        }

        // Fetch analysis
        const analysisRes = await apiGetAnalysis(matchId);
        if (analysisRes.ok) {
          setAnalysis(analysisRes.data);
        }

        // Fetch alerts
        const alertsRes = await apiGetAlerts(matchId);
        if (alertsRes.ok) {
          setAlerts(alertsRes.data);
        } else {
          setAlerts(mockAlerts.filter((a) => a.matchId === matchId) as TacticalAlert[]);
        }

        // Fetch video
        const videoRes = await apiGetMatchVideo(matchId);
        if (videoRes.ok) {
          setVideo(videoRes.data);
        }

        // Fetch players for featured section
        const playersRes = await apiGetScoutingPlayers();
        if (playersRes.ok) {
          setPlayers(playersRes.data);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        const fallback = mockMatches.find((m) => m.id === matchId);
        setMatch(fallback as Match);
      } finally {
        setLoading(false);
      }
    };

    if (Number.isFinite(matchId)) {
      fetchData();
    }
  }, [matchId]);

  const effectiveMatch = match || mockMatches.find((m) => m.id === matchId) || mockMatches[0];

  const timelineItems: TimelineItem[] = useMemo(
    () => [
      { id: "t1", title: "Yükleme tamamlandı", timeLabel: "07:30", tone: "success" },
      { id: "t2", title: "Kalibrasyon", timeLabel: "07:50", tone: "accent" },
      { id: "t3", title: "Taktik metrikler", timeLabel: "08:20", tone: "warning" },
      { id: "t4", title: "Rapor üretimi", timeLabel: "09:05", tone: "accent" },
    ],
    [],
  );

  const idStr = String(Number.isFinite(matchId) ? matchId : idParam);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center text-text-muted">Yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="text-sm text-emerald-200/80">Maç #{idStr}</div>
          <h1 className="mt-1 text-2xl font-semibold text-white">{effectiveMatch.opponentName}</h1>
          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge status={effectiveMatch.status} />
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-text-muted">
              {effectiveMatch.ageCategory} • {effectiveMatch.gameFormat}
            </span>
          </div>
          <div className="mt-3 text-sm text-text-muted">
            Skor: <span className="text-white font-semibold">{effectiveMatch.scoreFor}:{effectiveMatch.scoreAgainst}</span>
          </div>
        </div>

        <div className="rounded-2xl pv-card p-4 w-full md:w-80">
          <div className="text-sm font-semibold text-white">Hızlı geçiş</div>
          <div className="mt-3 flex flex-wrap gap-2">
            {subTabs.map((t) => (
              <Link
                key={t.key}
                href={t.href(idStr)}
                className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-text-muted hover:text-white hover:border-emerald-400/40"
              >
                {t.label}
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Analysis Metrics */}
      {analysis && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl pv-card p-4">
            <div className="text-xs text-text-muted">Top Hakimiyeti (Ev)</div>
            <div className="mt-2 text-2xl font-bold text-emerald-400">{analysis.possession_home?.toFixed(1)}%</div>
          </div>
          <div className="rounded-2xl pv-card p-4">
            <div className="text-xs text-text-muted">Top Hakimiyeti (Deplasman)</div>
            <div className="mt-2 text-2xl font-bold text-emerald-400">{analysis.possession_away?.toFixed(1)}%</div>
          </div>
          <div className="rounded-2xl pv-card p-4">
            <div className="text-xs text-text-muted">Şut (Ev)</div>
            <div className="mt-2 text-2xl font-bold text-emerald-400">{analysis.shots_home}</div>
          </div>
          <div className="rounded-2xl pv-card p-4">
            <div className="text-xs text-text-muted">Şut (Deplasman)</div>
            <div className="mt-2 text-2xl font-bold text-emerald-400">{analysis.shots_away}</div>
          </div>
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <Timeline items={timelineItems} />
          <div className="grid gap-4 sm:grid-cols-2">
            {/* Real alerts from API */}
            {alerts.length > 0 ? (
              alerts.slice(0, 2).map((a: any) => (
                <AlertCard key={a.id} alert={a} />
              ))
            ) : (
              <div className="text-text-muted text-sm">Uyarı bulunamadı</div>
            )}
          </div>
        </div>

        <div className="lg:col-span-1 space-y-4">
          <div className="rounded-2xl pv-card p-5">
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold text-white">Video</div>
              <div className="text-xs text-text-muted">{video?.status ?? "—"}</div>
            </div>
            <div className="mt-4">
              {video?.storagePath ? (
                <VideoPlayer src={video.storagePath} title={video.fileName || "Maç videosu"} />
              ) : (
                <div className="rounded-xl bg-white/5 border border-white/10 p-8 text-center text-sm text-text-muted">
                  Video henüz yüklenmedi
                </div>
              )}
            </div>
          </div>

          <div className="rounded-2xl pv-card p-5">
            <div className="text-sm font-semibold text-white">Öne çıkan oyuncular</div>
            <div className="mt-3 space-y-3">
              {players.slice(0, 2).map((p) => (
                <div key={p.id} className="flex items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-3">
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-white truncate">{p.firstName} {p.lastName}</div>
                    <div className="text-xs text-text-muted">{p.position}</div>
                  </div>
                  <div className="text-xs text-text-muted">{(p.developmentVelocity ?? 0).toFixed(2)}</div>
                </div>
              ))}
              {players.length === 0 && (
                <div className="text-xs text-text-muted">Oyuncu verisi yükleniyor...</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

