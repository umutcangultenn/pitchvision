"use client";

import { useApi, useMutation } from "@/hooks/useApi";
import {
  apiGetMatches,
  apiGetMatchById,
  apiGetMatchSummary,
  apiGetProcessingStatus,
  apiStartProcessing,
  apiGetMatchVideo,
  apiGetAlerts,
  apiGetClips,
  apiGetMetrics,
  apiGetMatchReport,
  apiCreateMatchReport,
  apiGetMatchDrills,
} from "@/lib/api";

export function useMatches(orgId?: number) {
  return useApi(() => apiGetMatches(orgId), { deps: [orgId] });
}

export function useMatch(matchId: number | undefined) {
  return useApi(
    () => apiGetMatchById(matchId!),
    { skip: !matchId, deps: [matchId] },
  );
}

export function useMatchSummary(matchId: number | undefined) {
  return useApi(
    () => apiGetMatchSummary(matchId!),
    { skip: !matchId, deps: [matchId] },
  );
}

export function useMatchVideo(matchId: number | undefined) {
  return useApi(
    () => apiGetMatchVideo(matchId!),
    { skip: !matchId, deps: [matchId] },
  );
}

export function useProcessingStatus(matchId: number | undefined) {
  return useApi(
    () => apiGetProcessingStatus(matchId!),
    { skip: !matchId, deps: [matchId] },
  );
}

export function useStartProcessing() {
  return useMutation((matchId: number) => apiStartProcessing(matchId));
}

export function useMatchAlerts(matchId: number | undefined) {
  return useApi(
    () => apiGetAlerts(matchId!),
    { skip: !matchId, deps: [matchId] },
  );
}

export function useMatchClips(matchId: number | undefined) {
  return useApi(
    () => apiGetClips(matchId!),
    { skip: !matchId, deps: [matchId] },
  );
}

export function useMatchMetrics(matchId: number | undefined) {
  return useApi(
    () => apiGetMetrics(matchId!),
    { skip: !matchId, deps: [matchId] },
  );
}

export function useMatchReport(matchId: number | undefined) {
  return useApi(
    () => apiGetMatchReport(matchId!),
    { skip: !matchId, deps: [matchId] },
  );
}

export function useCreateMatchReport() {
  return useMutation((matchId: number) => apiCreateMatchReport(matchId));
}

export function useMatchDrills(matchId: number | undefined) {
  return useApi(
    () => apiGetMatchDrills(matchId!),
    { skip: !matchId, deps: [matchId] },
  );
}
