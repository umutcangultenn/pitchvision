'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'next/navigation';
import SegmentTimeline from '@/components/Analysis/SegmentTimeline';
import EventTagger from '@/components/Analysis/EventTagger';
import ComparisonView from '@/components/Analysis/ComparisonView';
import AISummaryCard from '@/components/Analysis/AISummaryCard';
import VideoPlayer, { VideoPlayerHandle } from '@/components/Analysis/VideoPlayer';
import {
  matchApi,
  segmentApi,
  engineEventApi,
  analystEventApi,
  comparisonApi,
  aiApi,
  type MatchData,
  type MatchSegment,
  type EngineEvent,
  type AnalystEvent,
  type ComparisonResult,
  type AnalystEventCreate,
} from '@/lib/api';

// ── Tab definitions ───────────────────────────────────────────────────────────

const TABS = [
  { id: 'overview',    label: 'Genel Bakış' },
  { id: 'ai_analysis', label: 'Yapay Zeka Analizi' },
  { id: 'my_notes',    label: 'Notlarım (Tagger)' },
  { id: 'comparison',  label: 'Karşılaştırma (AI vs Analist)' },
] as const;

type TabId = (typeof TABS)[number]['id'];

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatTimestamp(seconds: number): string {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = Math.floor(seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

function eventTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    dangerous_attack:   'Tehlikeli Atak',
    rapid_transition:   'Hızlı Geçiş',
    box_entry:          'Ceza Sahası Girişi',
    pressure_moment:    'Baskı Anı',
    attacking_overload: 'Hücum Yığılması',
    wing_overload:      'Kanat Yığılması',
    compactness_issue:  'Kompaktlık Sorunu',
    counter_attack:     'Kontratak',
    possession_loss:    'Top Kaybı',
    possession_regain:  'Top Kazanma',
    defensive_breakdown:'Savunma Zafiyeti',
    shot:               'Şut',
    goal:               'Gol',
  };
  return labels[type] ?? type;
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function MatchDetailPage() {
  const params = useParams();
  const matchId = Number(params.id);

  const videoRef = useRef<VideoPlayerHandle>(null);

  const [activeTab, setActiveTab]           = useState<TabId>('overview');
  const [activeSegmentId, setActiveSegmentId] = useState<number | null>(null);
  const [videoTimestamp, setVideoTimestamp] = useState<number>(0);

  // Data states
  const [matchData,      setMatchData]      = useState<MatchData | null>(null);
  const [segments,       setSegments]       = useState<MatchSegment[]>([]);
  const [engineEvents,   setEngineEvents]   = useState<EngineEvent[]>([]);
  const [analystEvents,  setAnalystEvents]  = useState<AnalystEvent[]>([]);
  const [comparisonData, setComparisonData] = useState<ComparisonResult | null>(null);
  const [aiSummary,      setAiSummary]      = useState<string>('');

  // Loading / error states
  const [loadingMatch,      setLoadingMatch]      = useState(true);
  const [loadingSegments,   setLoadingSegments]   = useState(true);
  const [loadingEvents,     setLoadingEvents]     = useState(true);
  const [loadingAnalyst,    setLoadingAnalyst]    = useState(true);
  const [loadingComparison, setLoadingComparison] = useState(true);
  const [loadingAI,         setLoadingAI]         = useState(false);
  const [savingEvent,       setSavingEvent]       = useState(false);

  const [errorMatch,      setErrorMatch]      = useState<string | null>(null);
  const [errorSegments,   setErrorSegments]   = useState<string | null>(null);
  const [errorEvents,     setErrorEvents]     = useState<string | null>(null);
  const [errorAnalyst,    setErrorAnalyst]    = useState<string | null>(null);
  const [errorComparison, setErrorComparison] = useState<string | null>(null);
  const [errorAI,         setErrorAI]         = useState<string | null>(null);

  // ── Data fetching ───────────────────────────────────────────────────────────

  useEffect(() => {
    if (!matchId) return;

    setLoadingMatch(true);
    matchApi.getById(matchId)
      .then(setMatchData)
      .catch((e: Error) => setErrorMatch(e.message))
      .finally(() => setLoadingMatch(false));

    setLoadingSegments(true);
    segmentApi.getByMatch(matchId)
      .then(setSegments)
      .catch((e: Error) => setErrorSegments(e.message))
      .finally(() => setLoadingSegments(false));

    setLoadingEvents(true);
    engineEventApi.getByMatch(matchId)
      .then(setEngineEvents)
      .catch((e: Error) => setErrorEvents(e.message))
      .finally(() => setLoadingEvents(false));

    setLoadingAnalyst(true);
    analystEventApi.getByMatch(matchId)
      .then(setAnalystEvents)
      .catch((e: Error) => setErrorAnalyst(e.message))
      .finally(() => setLoadingAnalyst(false));

    setLoadingComparison(true);
    comparisonApi.getByMatch(matchId)
      .then(setComparisonData)
      .catch(() => setComparisonData(null))   // 404 is expected — not an error
      .finally(() => setLoadingComparison(false));
  }, [matchId]);

  // ── AI Summary (lazy — triggered when tab is opened) ───────────────────────

  const fetchAISummary = useCallback(async () => {
    if (aiSummary || loadingAI) return;
    setLoadingAI(true);
    setErrorAI(null);
    try {
      const res = await aiApi.matchSummary(matchId);
      setAiSummary(res.draft);
    } catch (e: unknown) {
      setErrorAI(e instanceof Error ? e.message : 'Özet alınamadı.');
    } finally {
      setLoadingAI(false);
    }
  }, [matchId, aiSummary, loadingAI]);

  useEffect(() => {
    if (activeTab === 'ai_analysis') {
      fetchAISummary();
    }
  }, [activeTab, fetchAISummary]);

  // ── Event handlers ──────────────────────────────────────────────────────────

  /** Seek the video player to a specific second. */
  const handleSeekTo = useCallback((seconds: number) => {
    videoRef.current?.seekTo(seconds);
    // Switch to overview tab so the analyst can see the video
    setActiveTab('overview');
  }, []);

  /** Save a new analyst event via the API. */
  const handleSaveEvent = useCallback(async (eventData: {
    tag: string;
    timestamp_seconds: number;
    notes: string;
    confidence: string;
  }) => {
    setSavingEvent(true);
    try {
      const payload: AnalystEventCreate = {
        match_id: matchId,
        tag: eventData.tag,
        timestamp_seconds: eventData.timestamp_seconds,
        notes: eventData.notes || undefined,
        confidence: eventData.confidence,
      };
      const created = await analystEventApi.create(payload);
      setAnalystEvents((prev) => [...prev, created]);
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'Olay kaydedilemedi.');
    } finally {
      setSavingEvent(false);
    }
  }, [matchId]);

  /** Generate (or regenerate) the AI vs Analyst comparison. */
  const handleGenerateComparison = useCallback(async () => {
    setLoadingComparison(true);
    setErrorComparison(null);
    try {
      const result = await comparisonApi.generate(matchId);
      setComparisonData(result);
    } catch (e: unknown) {
      setErrorComparison(e instanceof Error ? e.message : 'Karşılaştırma oluşturulamadı.');
    } finally {
      setLoadingComparison(false);
    }
  }, [matchId]);

  // ── Derived data ────────────────────────────────────────────────────────────

  const visibleEngineEvents = activeSegmentId
    ? engineEvents.filter((e) => e.segment_id === activeSegmentId)
    : engineEvents;

  // ── Loading / error guards ──────────────────────────────────────────────────

  if (loadingMatch) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-3" />
          <p className="text-gray-500 text-sm">Maç bilgileri yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (errorMatch || !matchData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-md">
          <p className="text-red-600 font-medium mb-2">Maç yüklenemedi</p>
          <p className="text-gray-500 text-sm">{errorMatch ?? 'Bilinmeyen hata'}</p>
        </div>
      </div>
    );
  }

  const matchTitle = `${matchData.home_away === 'Ev Sahibi' ? 'vs' : '@'} ${matchData.opponent_name}`;

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      {/* Header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{matchTitle}</h1>
          <p className="text-sm text-gray-500 mt-1">
            {new Date(matchData.match_date).toLocaleDateString('tr-TR', {
              day: 'numeric', month: 'long', year: 'numeric',
            })}
            {' · '}
            {matchData.location}
          </p>
        </div>
        <span className={`
          inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold
          ${matchData.status === 'completed'
            ? 'bg-green-100 text-green-800'
            : matchData.status === 'analyzing'
            ? 'bg-blue-100 text-blue-800'
            : 'bg-gray-100 text-gray-600'}
        `}>
          {matchData.status.toUpperCase()}
        </span>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8 overflow-x-auto" aria-label="Sekmeler">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
              `}
              aria-current={activeTab === tab.id ? 'page' : undefined}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">

        {/* ── Overview Tab ─────────────────────────────────────────────────── */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <VideoPlayer
              ref={videoRef}
              videoUrl={matchData.video_url}
              onTimeUpdate={setVideoTimestamp}
            />

            {/* Quick stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: 'Rakip',       value: matchData.opponent_name },
                { label: 'Süre',        value: `${matchData.duration_minutes} dk` },
                { label: 'AI Olayları', value: loadingEvents ? '…' : String(engineEvents.length) },
                { label: 'Notlarım',    value: loadingAnalyst ? '…' : String(analystEvents.length) },
              ].map((stat) => (
                <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">{stat.label}</p>
                  <p className="mt-1 text-lg font-bold text-gray-900">{stat.value}</p>
                </div>
              ))}
            </div>

            {/* Segment timeline preview */}
            {!loadingSegments && segments.length > 0 && (
              <SegmentTimeline
                segments={segments}
                activeSegmentId={activeSegmentId}
                onSelectSegment={(id) => {
                  setActiveSegmentId(id);
                  setActiveTab('ai_analysis');
                }}
              />
            )}
          </div>
        )}

        {/* ── AI Analysis Tab ───────────────────────────────────────────────── */}
        {activeTab === 'ai_analysis' && (
          <div className="space-y-6">

            {/* Segment timeline */}
            {loadingSegments ? (
              <div className="h-24 bg-gray-50 rounded-xl animate-pulse" />
            ) : errorSegments ? (
              <p className="text-red-500 text-sm">{errorSegments}</p>
            ) : (
              <SegmentTimeline
                segments={segments}
                activeSegmentId={activeSegmentId}
                onSelectSegment={setActiveSegmentId}
              />
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

              {/* Engine events list */}
              <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-gray-800">
                    {activeSegmentId ? `Segment Olayları` : 'Tüm AI Tespitleri'}
                  </h3>
                  {activeSegmentId && (
                    <button
                      onClick={() => setActiveSegmentId(null)}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      Tümünü göster
                    </button>
                  )}
                </div>

                {loadingEvents ? (
                  <div className="p-5 space-y-3">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="h-12 bg-gray-100 rounded animate-pulse" />
                    ))}
                  </div>
                ) : errorEvents ? (
                  <p className="p-5 text-red-500 text-sm">{errorEvents}</p>
                ) : visibleEngineEvents.length === 0 ? (
                  <p className="p-5 text-gray-400 text-sm italic">
                    {activeSegmentId ? 'Bu segmentte tespit yok.' : 'Henüz AI tespiti yok.'}
                  </p>
                ) : (
                  <ul className="divide-y divide-gray-50 max-h-96 overflow-y-auto">
                    {visibleEngineEvents.map((ev) => (
                      <li key={ev.id} className="px-5 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors">
                        <div className="flex items-center gap-3 min-w-0">
                          <span className="font-mono text-xs text-gray-400 shrink-0">
                            {formatTimestamp(ev.timestamp_seconds)}
                          </span>
                          <div className="min-w-0">
                            <p className="text-sm font-medium text-gray-800 truncate">
                              {eventTypeLabel(ev.event_type)}
                            </p>
                            <p className="text-xs text-gray-500 truncate">{ev.description}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 shrink-0 ml-3">
                          <span className="text-xs text-gray-400">
                            %{Math.round(ev.confidence * 100)}
                          </span>
                          <button
                            onClick={() => handleSeekTo(ev.timestamp_seconds)}
                            title="Videoda bu ana git"
                            className="p-1.5 rounded-md text-blue-500 hover:bg-blue-50 transition-colors"
                            aria-label={`${formatTimestamp(ev.timestamp_seconds)} anına git`}
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* AI Summary */}
              <div>
                {loadingAI ? (
                  <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
                      <span className="text-sm text-gray-500">Taktiksel özet oluşturuluyor...</span>
                    </div>
                    <div className="space-y-2">
                      {[1, 2, 3].map((i) => (
                        <div key={i} className="h-3 bg-gray-100 rounded animate-pulse" />
                      ))}
                    </div>
                  </div>
                ) : errorAI ? (
                  <div className="bg-white rounded-xl border border-red-200 p-5 shadow-sm">
                    <p className="text-sm text-red-600 mb-2">Özet alınamadı</p>
                    <p className="text-xs text-gray-500 mb-3">{errorAI}</p>
                    <button
                      onClick={() => { setAiSummary(''); fetchAISummary(); }}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      Tekrar dene
                    </button>
                  </div>
                ) : (
                  <AISummaryCard title="Taktiksel Taslak" content={aiSummary} />
                )}
              </div>
            </div>
          </div>
        )}

        {/* ── My Notes Tab ─────────────────────────────────────────────────── */}
        {activeTab === 'my_notes' && (
          <div className="space-y-6">
            <div className="max-w-2xl mx-auto">
              <EventTagger
                currentTimestamp={videoTimestamp}
                onSaveEvent={handleSaveEvent}
                isSaving={savingEvent}
              />
            </div>

            {/* Analyst events list */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="px-5 py-4 border-b border-gray-100">
                <h3 className="text-sm font-semibold text-gray-800">
                  Kaydedilen Notlar ({analystEvents.length})
                </h3>
              </div>

              {loadingAnalyst ? (
                <div className="p-5 space-y-3">
                  {[1, 2].map((i) => (
                    <div key={i} className="h-10 bg-gray-100 rounded animate-pulse" />
                  ))}
                </div>
              ) : errorAnalyst ? (
                <p className="p-5 text-red-500 text-sm">{errorAnalyst}</p>
              ) : analystEvents.length === 0 ? (
                <p className="p-5 text-gray-400 text-sm italic">Henüz not eklenmedi.</p>
              ) : (
                <ul className="divide-y divide-gray-50 max-h-80 overflow-y-auto">
                  {analystEvents.map((ev) => (
                    <li key={ev.id} className="px-5 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-3 min-w-0">
                        <span className="font-mono text-xs text-gray-400 shrink-0">
                          {formatTimestamp(ev.timestamp_seconds)}
                        </span>
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-gray-800">{ev.tag}</p>
                          {ev.notes && (
                            <p className="text-xs text-gray-500 truncate">{ev.notes}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0 ml-3">
                        <span className="text-xs text-gray-400">{ev.confidence}</span>
                        <button
                          onClick={() => handleSeekTo(ev.timestamp_seconds)}
                          title="Videoda bu ana git"
                          className="p-1.5 rounded-md text-blue-500 hover:bg-blue-50 transition-colors"
                          aria-label={`${formatTimestamp(ev.timestamp_seconds)} anına git`}
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}

        {/* ── Comparison Tab ────────────────────────────────────────────────── */}
        {activeTab === 'comparison' && (
          <div className="space-y-4">
            {loadingComparison ? (
              <div className="space-y-4">
                <div className="h-32 bg-gray-50 rounded-xl animate-pulse" />
                <div className="h-48 bg-gray-50 rounded-xl animate-pulse" />
              </div>
            ) : errorComparison ? (
              <div className="text-center p-8 bg-red-50 rounded-xl border border-red-200">
                <p className="text-red-600 text-sm">{errorComparison}</p>
                <button
                  onClick={handleGenerateComparison}
                  className="mt-3 text-sm text-blue-600 hover:underline"
                >
                  Tekrar dene
                </button>
              </div>
            ) : (
              <>
                <ComparisonView
                  comparisonData={comparisonData}
                  onSeekTo={handleSeekTo}
                />
                <div className="flex justify-end">
                  <button
                    onClick={handleGenerateComparison}
                    disabled={loadingComparison}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Karşılaştırmayı Yenile
                  </button>
                </div>
              </>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
