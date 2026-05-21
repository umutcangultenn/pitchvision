"use client";

import React from "react";

import { mockMatches, mockPlayers, mockMetrics, mockAlerts, mockReports, mockClips, mockDrills } from "@/data/demo";

import { StatCard } from "@/components/cards/StatCard";
import { TacticalMetricCard } from "@/components/cards/TacticalMetricCard";
import { MatchCard } from "@/components/cards/MatchCard";
import { PlayerCard } from "@/components/cards/PlayerCard";
import { AlertCard } from "@/components/cards/AlertCard";
import { ReportCard } from "@/components/cards/ReportCard";
import { VideoClipCard } from "@/components/cards/VideoClipCard";
import { DrillRecommendationCard } from "@/components/cards/DrillRecommendationCard";
import { ScoutNoteCard } from "@/components/cards/ScoutNoteCard";

import { FilterBar } from "@/components/ui/FilterBar";
import { ConfidenceBadge } from "@/components/ui/ConfidenceBadge";
import { SeverityBadge } from "@/components/ui/SeverityBadge";
import { StatusBadge } from "@/components/ui/StatusBadge";

import { mockScoutingNotes } from "@/data/demo";

export default function ComponentsPage() {
  const match = mockMatches[0];
  const metric = mockMetrics[0] as any;
  const player = mockPlayers[0];
  const alert = mockAlerts[0] as any;
  const report = mockReports[0];
  const clip = (mockClips as any)[0];
  const drill = mockDrills[0];
  const note = mockScoutingNotes[0] as any;

  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm font-medium text-emerald-200/80">Components</div>
        <h1 className="mt-1 text-2xl font-semibold text-white">Component katalog</h1>
        <p className="mt-2 text-sm text-text-muted">Mock data ile bileşenlerin görünümünü kontrol edin.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <StatCard title="Stat örneği" value="0.74" footer="Premium kart" />
        <TacticalMetricCard metric={metric} />
        <MatchCard match={match as any} />
        <PlayerCard player={player as any} />
        <AlertCard alert={alert} />
        <ReportCard report={report as any} />
        <VideoClipCard clip={clip} />
        <DrillRecommendationCard drill={drill as any} />
        <ScoutNoteCard note={note} />
      </div>

      <section className="rounded-2xl pv-card p-5">
        <div className="text-sm font-semibold text-white">Badge & Filter</div>
        <div className="mt-4 flex flex-wrap gap-3">
          <StatusBadge status="completed" />
          <ConfidenceBadge value={0.73} />
          <SeverityBadge severity="medium" />
        </div>
        <div className="mt-4">
          <FilterBar
            left={<input className="w-72 max-w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40" placeholder="Filtre" />}
            right={<div className="text-sm text-text-muted">Toplam: 3</div>}
          />
        </div>
      </section>
    </div>
  );
}

