"use client";

import React, { useMemo } from "react";

import { useAppStore } from "@/lib/appStore";
import { mockOrganizations, mockTeams } from "@/data/demo";

export function OrgTeamSeasonSelector() {
  const { organizationId, teamId, season, setOrganizationId, setTeamId, setSeason } = useAppStore();

  const org = useMemo(() => mockOrganizations.find((o) => o.id === organizationId), [organizationId]);
  const teams = useMemo(() => mockTeams.filter((t) => t.organizationId === organizationId), [organizationId]);

  const selectedTeam = useMemo(() => mockTeams.find((t) => t.id === teamId), [teamId]);
  const seasons = useMemo(() => Array.from(new Set(teams.map((t) => t.season))), [teams]);

  return (
    <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:gap-3">
      <div className="text-xs text-text-muted">Kulüp / Takım / Sezon</div>
      <div className="flex gap-2">
        <select
          value={organizationId}
          onChange={(e) => setOrganizationId(Number(e.target.value))}
          className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
        >
          {mockOrganizations.map((o) => (
            <option key={o.id} value={o.id} className="bg-[#0a0f0d]">
              {o.name}
            </option>
          ))}
        </select>

        <select
          value={teamId}
          onChange={(e) => setTeamId(Number(e.target.value))}
          className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
        >
          {teams.map((t) => (
            <option key={t.id} value={t.id} className="bg-[#0a0f0d]">
              {t.name}
            </option>
          ))}
        </select>

        <select
          value={season}
          onChange={(e) => setSeason(e.target.value)}
          className="hidden md:block rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
        >
          {seasons.map((s) => (
            <option key={s} value={s} className="bg-[#0a0f0d]">
              {s}
            </option>
          ))}
        </select>
      </div>

      <div className="hidden sm:flex flex-wrap gap-2 text-xs text-text-muted">
        <span>{org?.name}</span>
        <span className="opacity-60">•</span>
        <span>{selectedTeam?.name}</span>
        <span className="opacity-60">•</span>
        <span>{season}</span>
      </div>
    </div>
  );
}

