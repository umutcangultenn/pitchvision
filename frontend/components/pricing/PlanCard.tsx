"use client";

import Link from "next/link";
import React from "react";

import type { SaaSPlan } from "@/lib/pricing";

const rows: { key: keyof Pick<
  SaaSPlan,
  | "monthlyMatchAnalysis"
  | "playerSlots"
  | "videoStorage"
  | "reportExport"
  | "scoutingModule"
  | "premiumSupport"
>; label: string }[] = [
  { key: "monthlyMatchAnalysis", label: "Aylık maç analizi hakkı" },
  { key: "playerSlots", label: "Oyuncu sayısı" },
  { key: "videoStorage", label: "Video depolama" },
  { key: "reportExport", label: "Rapor export" },
  { key: "scoutingModule", label: "Scouting modülü" },
  { key: "premiumSupport", label: "Premium destek" },
];

export function PlanCard({
  plan,
  onSelectPlan,
}: {
  plan: SaaSPlan;
  onSelectPlan?: (planId: string) => void;
}) {
  const demoHref = `/demo-request?plan=${encodeURIComponent(plan.id)}`;
  const selectHref = `${demoHref}&intent=select`;

  return (
    <div
      className={`relative flex flex-col rounded-2xl border p-6 transition ${
        plan.recommended
          ? "border-emerald-400/45 bg-gradient-to-b from-emerald-500/15 to-white/[0.04] shadow-lg shadow-emerald-900/20"
          : "border-white/10 bg-white/[0.03]"
      }`}
    >
      {plan.recommended ? (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-emerald-500 px-3 py-0.5 text-xs font-semibold text-white">
          Çoğu akademi için uygun
        </div>
      ) : null}

      <div className="mt-1">
        <h2 className="text-lg font-semibold text-white">{plan.name}</h2>
        <p className="mt-2 text-sm leading-relaxed text-text-muted">{plan.tagline}</p>
      </div>

      <div className="mt-5 space-y-2.5 border-t border-white/10 pt-5">
        {rows.map((r) => (
          <div key={r.key} className="flex justify-between gap-3 text-sm">
            <span className="text-text-muted">{r.label}</span>
            <span className="max-w-[55%] text-right font-medium text-white/90">{plan[r.key]}</span>
          </div>
        ))}
      </div>

      <div className="mt-6 border-t border-white/10 pt-5">
        <div className="text-2xl font-bold text-emerald-200/95">{plan.pricePlaceholder}</div>
        <p className="mt-1 text-xs text-text-muted">Kesin fiyat için demo sonrası teklif paylaşılır.</p>
      </div>

      <div className="mt-6 flex flex-col gap-2 sm:flex-row">
        <Link
          href={demoHref}
          className="inline-flex flex-1 items-center justify-center rounded-xl border border-white/15 bg-white/5 px-4 py-2.5 text-center text-sm font-semibold text-white hover:border-emerald-400/40 hover:bg-white/10"
        >
          Demo Talep Et
        </Link>
        <Link
          href={selectHref}
          onClick={() => onSelectPlan?.(plan.id)}
          className="inline-flex flex-1 items-center justify-center rounded-xl bg-emerald-600 px-4 py-2.5 text-center text-sm font-semibold text-white hover:bg-emerald-500"
        >
          Planı Seç
        </Link>
      </div>
    </div>
  );
}
