"use client";

import { useApi, useMutation } from "@/hooks/useApi";
import {
  apiGetPlayers,
  apiGetPlayerById,
  apiGetPlayerPassport,
  apiGetPlayerPerformances,
  apiGetPlayerClips,
  apiGetScoutingNotes,
  apiCreateScoutNote,
  apiGetScoutingPlayers,
  apiGetHiddenGems,
} from "@/lib/api";

export function usePlayers(orgId?: number) {
  return useApi(() => apiGetPlayers(orgId), { deps: [orgId] });
}

export function usePlayer(playerId: number | undefined) {
  return useApi(
    () => apiGetPlayerById(playerId!),
    { skip: !playerId, deps: [playerId] },
  );
}

export function usePlayerPassport(playerId: number | undefined) {
  return useApi(
    () => apiGetPlayerPassport(playerId!),
    { skip: !playerId, deps: [playerId] },
  );
}

export function usePlayerPerformances(playerId: number | undefined) {
  return useApi(
    () => apiGetPlayerPerformances(playerId!),
    { skip: !playerId, deps: [playerId] },
  );
}

export function usePlayerClips(playerId: number | undefined) {
  return useApi(
    () => apiGetPlayerClips(playerId!),
    { skip: !playerId, deps: [playerId] },
  );
}

export function useScoutNotes(playerId: number | undefined) {
  return useApi(
    () => apiGetScoutingNotes(playerId!),
    { skip: !playerId, deps: [playerId] },
  );
}

export function useCreateScoutNote() {
  return useMutation(({ playerId, note, rating, tagsJson }: { playerId: number; note: string; rating?: number; tagsJson?: string[] }) =>
    apiCreateScoutNote(playerId, note, rating, tagsJson),
  );
}

export function useScoutingPlayers() {
  return useApi(() => apiGetScoutingPlayers());
}

export function useHiddenGems() {
  return useApi(() => apiGetHiddenGems());
}
