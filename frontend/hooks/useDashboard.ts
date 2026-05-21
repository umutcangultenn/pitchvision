"use client";

import { useApi } from "@/hooks/useApi";
import { apiGetDashboard } from "@/lib/api";

export function useDashboard(orgId?: number) {
  return useApi(() => apiGetDashboard(orgId), { deps: [orgId] });
}
