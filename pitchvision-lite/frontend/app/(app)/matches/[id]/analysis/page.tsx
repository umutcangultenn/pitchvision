"use client";

import React, { useMemo, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

import { mockMatches, mockVideos, mockAlerts, mockClips, mockPlayers, mockPerformances, demoVideoSrc } from "@/data/demo";
import { AnalysisVideoPlayer } from "@/components/video/AnalysisVideoPlayer";
import { MetricsTab } from "@/components/analysis/MetricsTab";
import { AlertsTab } from "@/components/analysis/AlertsTab";
import { ClipsTab } from "@/components/analysis/ClipsTab";
import { PlayersTab } from "@/components/analysis/PlayersTab";
import { NotesTab } from "@/components/analysis/NotesTab";
import { VideoTimeline } from "@/components/analysis/VideoTimeline";
import { CreateClipModal } from "@/components/modals/CreateClipModal";
import { AddNoteModal } from "@/components/modals/AddNoteModal";
import type { OverlayType, VideoEvent, TeamMetrics } from "@/types/domain";

type TabType = "metrics" | "alerts" | "clips" | "players" | "notes";

export default function MatchAnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const idParam = String(params.id);
  const matchId = Number(idParam);
  const isDemo = idParam === "demo-match" || !Number.isFinite(matchId);

  const match = useMemo(() => {
    if (isDemo) return null;
    return mockMatches.find((m) => m.id === matchId) ?? null;
  }, [matchId, isDemo]);

  const video = useMemo(() => {
    if (isDemo) return null;
    return mockVideos.find((v) => v.matchId === matchId) ?? null;
  }, [matchId, isDemo]);

  // State
  const [currentTime, setCurrentTime] = useState(0);
  const [activeTab, setActiveTab] = useState<TabType>("metrics");
  const [overlays, setOverlays] = useState<OverlayType[]>(["players", "formation"]);
  const [showCreateClipModal, setShowCreateClipModal] = useState(false);
  const [showAddNoteModal, setShowAddNoteModal] = useState(false);
  const [notes, setNotes] = useState<any[]>([]);

  // Mock data
  const duration = video?.durationSeconds || 5400; // 90 minutes
  const matchLabel = isDemo
    ? "Demo Maç"
    : match
    ? `${match.opponentName} (${new Date(match.matchDate).toLocaleDateString("tr-TR")})`
    : `Maç #${idParam}`;

  const teamMetrics: TeamMetrics = {
    teamLength: 47.2,
    teamWidth: 42.8,
    compactness: 18.4,
    defenseToMidfieldDistance: 21.4,
    midfieldToAttackDistance: 16.8,
    transitionSpeed: 4.6
  };

  const alerts = useMemo(() => 
    mockAlerts.filter(a => isDemo || a.matchId === matchId), 
    [matchId, isDemo]
  );

  const clips = useMemo(() => 
    mockClips.filter(c => isDemo || c.matchId === matchId), 
    [matchId, isDemo]
  );

  const players = useMemo(() => 
    mockPlayers.filter(p => isDemo || p.teamId === match?.teamId), 
    [match?.teamId, isDemo]
  );

  const performances = useMemo(() => 
    mockPerformances.filter(p => isDemo || p.matchId === matchId), 
    [matchId, isDemo]
  );

  // Generate timeline events
  const timelineEvents: VideoEvent[] = useMemo(() => {
    const events: VideoEvent[] = [];
    
    // Add alerts as events
    alerts.forEach(alert => {
      events.push({
        id: `alert-${alert.id}`,
        type: "alert",
        timestamp: alert.startTime,
        title: alert.title,
        description: alert.description,
        severity: alert.severity,
        confidence: alert.confidence
      });
    });

    // Add clips as events
    clips.forEach(clip => {
      events.push({
        id: `clip-${clip.id}`,
        type: "clip",
        timestamp: clip.startTime,
        title: clip.title,
        description: clip.description
      });
    });

    // Add some mock goals and cards
    if (isDemo) {
      events.push(
        {
          id: "goal-1",
          type: "goal",
          timestamp: 1234,
          title: "Gol - Kaan Yılmaz",
          description: "Sol kanattan içeri kesme sonrası şut"
        },
        {
          id: "card-1", 
          type: "card",
          timestamp: 2156,
          title: "Sarı Kart",
          description: "Efe Çelik - Geç müdahale"
        }
      );
    }

    return events.sort((a, b) => a.timestamp - b.timestamp);
  }, [alerts, clips, isDemo]);

  // Handlers
  const handleTimeUpdate = useCallback((time: number) => {
    setCurrentTime(time);
  }, []);

  const handleOverlayToggle = useCallback((overlay: OverlayType) => {
    setOverlays(prev => 
      prev.includes(overlay) 
        ? prev.filter(o => o !== overlay)
        : [...prev, overlay]
    );
  }, []);

  const handleCreateClip = useCallback((data: any) => {
    console.log("Creating clip:", data);
    // Mock clip creation
  }, []);

  const handleAddNote = useCallback((data: any) => {
    const newNote = {
      id: Date.now().toString(),
      ...data,
      author: "Antrenör",
      createdAt: new Date().toISOString()
    };
    setNotes(prev => [...prev, newNote]);
  }, []);

  const handleSeekToTime = useCallback((time: number) => {
    setCurrentTime(time);
  }, []);

  const handleEventClick = useCallback((event: VideoEvent) => {
    setCurrentTime(event.timestamp);
  }, []);

  const handleShowInVideo = useCallback((alertId: number, startTime: number) => {
    setCurrentTime(startTime);
  }, []);

  const tabs = [
    { key: "metrics" as TabType, label: "Metrikler", icon: "📊" },
    { key: "alerts" as TabType, label: "Uyarılar", icon: "⚠️", count: alerts.length },
    { key: "clips" as TabType, label: "Klipler", icon: "✂️", count: clips.length },
    { key: "players" as TabType, label: "Oyuncular", icon: "👥", count: players.length },
    { key: "notes" as TabType, label: "Notlar", icon: "📝", count: notes.length },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
        <div>
          <div className="text-sm text-text-muted">Video Analiz</div>
          <h1 className="mt-1 text-2xl font-semibold text-white">{matchLabel}</h1>
        </div>

        {/* Action bar */}
        <div className="flex gap-2 flex-wrap">
          <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-white/5 border border-white/10">
            <div className="text-xs text-text-muted">Kalibrasyon:</div>
            <div className="text-xs text-success">İyi (0.8m)</div>
          </div>
          <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-white/5 border border-white/10">
            <div className="text-xs text-text-muted">Tracking:</div>
            <div className="text-xs text-accent">%94 güven</div>
          </div>
          <Link
            href={`/matches/${idParam}/report`}
            className="px-4 py-2 rounded-lg text-sm font-medium bg-success/20 border border-success/40 text-success hover:bg-success/30 transition-all"
          >
            📄 Raporu Aç
          </Link>
          <button className="px-4 py-2 rounded-lg text-sm font-medium bg-warning/20 border border-warning/40 text-warning hover:bg-warning/30 transition-all">
            📥 PDF Export
          </button>
          <Link
            href={`/matches/${idParam}/calibration`}
            className="px-4 py-2 rounded-lg text-sm font-medium bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all"
          >
            📐 Kalibrasyon
          </Link>
          <button className="px-4 py-2 rounded-lg text-sm font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all">
            🔄 Yeniden Analiz Et
          </button>
        </div>
      </div>

      {/* Main layout */}
      <div className="grid gap-6 lg:grid-cols-4">
        {/* Left: Video player (3/4) */}
        <div className="lg:col-span-3 space-y-4">
          <AnalysisVideoPlayer
            src={demoVideoSrc}
            title={matchLabel}
            currentTime={currentTime}
            duration={duration}
            onTimeUpdate={handleTimeUpdate}
            onCreateClip={() => setShowCreateClipModal(true)}
            onAddNote={() => setShowAddNoteModal(true)}
            overlays={overlays}
            onOverlayToggle={handleOverlayToggle}
          />

          {/* Timeline */}
          <VideoTimeline
            duration={duration}
            currentTime={currentTime}
            events={timelineEvents}
            onSeek={handleSeekToTime}
            onEventClick={handleEventClick}
          />
        </div>

        {/* Right: Analysis panel (1/4) */}
        <div className="lg:col-span-1">
          <div className="rounded-2xl pv-card p-5 h-fit">
            {/* Tabs */}
            <div className="flex flex-col gap-1 mb-4">
              {tabs.map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    activeTab === tab.key
                      ? "bg-accent/20 border border-accent/40 text-accent"
                      : "bg-white/5 border border-white/10 text-text hover:bg-white/10"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span>{tab.icon}</span>
                    <span>{tab.label}</span>
                  </div>
                  {tab.count !== undefined && (
                    <span className="text-xs px-2 py-1 rounded bg-white/10">
                      {tab.count}
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Tab content */}
            <div className="min-h-96">
              {activeTab === "metrics" && <MetricsTab metrics={teamMetrics} />}
              {activeTab === "alerts" && (
                <AlertsTab
                  alerts={alerts}
                  onShowInVideo={handleShowInVideo}
                  onCreateClip={() => setShowCreateClipModal(true)}
                />
              )}
              {activeTab === "clips" && <ClipsTab clips={clips} onPlayClip={handleSeekToTime} />}
              {activeTab === "players" && (
                <PlayersTab
                  players={players}
                  performances={performances}
                />
              )}
              {activeTab === "notes" && (
                <NotesTab
                  notes={notes}
                  onAddNote={handleAddNote}
                  currentTime={currentTime}
                />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      <CreateClipModal
        isOpen={showCreateClipModal}
        onClose={() => setShowCreateClipModal(false)}
        onCreateClip={handleCreateClip}
        currentTime={currentTime}
      />

      <AddNoteModal
        isOpen={showAddNoteModal}
        onClose={() => setShowAddNoteModal(false)}
        onAddNote={handleAddNote}
        currentTime={currentTime}
      />
    </div>
  );
}