"use client";

import { create } from "zustand";

import type { Organization, Team } from "@/types/domain";
import { mockOrganizations, mockTeams } from "@/data/demo";

type SeasonId = string;

type AppState = {
  organizationId: number;
  teamId: number;
  season: SeasonId;
  setOrganizationId: (id: number) => void;
  setTeamId: (id: number) => void;
  setSeason: (season: SeasonId) => void;
};

const initialOrg = mockOrganizations[0] as Organization;
const initialTeam = mockTeams.find((t) => t.organizationId === initialOrg.id) ?? (mockTeams[0] as Team);

export const useAppStore = create<AppState>((set) => ({
  organizationId: initialOrg.id,
  teamId: initialTeam.id,
  season: initialTeam.season,
  setOrganizationId: (id) => set({ organizationId: id }),
  setTeamId: (id) => {
    const t = mockTeams.find((x) => x.id === id);
    set({ teamId: id, season: t?.season ?? "2025/26" });
  },
  setSeason: (season) => set({ season }),
}));

