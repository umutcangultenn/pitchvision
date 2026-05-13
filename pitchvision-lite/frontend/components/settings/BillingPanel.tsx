"use client";

import Link from "next/link";
import React from "react";

import { DEMO_SAAS_USAGE } from "@/lib/pricing";
import type { SubscriptionDto } from "@/lib/api";

function UsageBar({
  label,
  used,
  cap,
  unit,
}: {
  label: string;
  used: number;
  cap: number;
  unit?: string;
}) {
  const pct = cap > 0 ? Math.min(100, Math.round((used / cap) * 100)) : 0;
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-sm">
        <span className="text-text-muted">{label}</span>
        <span className="font-medium text-white">
          {used}
          {unit ? ` ${unit}` : ""} / {cap}
          {unit ? ` ${unit}` : ""}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-white/10">
        <div
          className={`h-full rounded-full transition-all ${
            pct >= 90 ? "bg-amber-500/80" : "bg-emerald-500/70"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export function BillingPanel({
  subscription,
  onPortalClick,
}: {
  subscription: SubscriptionDto;
  onPortalClick?: () => void;
}) {
  const u = DEMO_SAAS_USAGE;

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-white/10 bg-emerald-500/5 p-5 text-sm text-emerald-100/90">
        <p>
          Limitler, planınıza ve sezon yoğunluğunuza göre yumuşak hatırlatıcılar olarak gösterilir.
          Kesin kota ve faturalama için ekibimizle netleştirme yapılır; böylece saha gününde sürpriz
          yaşanmaz.
        </p>
      </div>

      <div className="rounded-2xl pv-card p-6">
        <div className="text-sm font-semibold text-white">Bu dönem kullanım özeti</div>
        <p className="mt-1 text-xs text-text-muted">
          Aşağıdaki rakamlar demo gösterimidir; gerçek ortamda API ile güncellenir.
        </p>
        <div className="mt-5 space-y-5">
          <UsageBar label="Bu ay işlenen maç" used={u.matchesUsed} cap={u.matchesCap} />
          <UsageBar label="Video depolama" used={u.storageUsedGb} cap={u.storageCapGb} unit="GB" />
          <UsageBar label="Oyuncu pasaportu (aktif)" used={u.passportUsed} cap={u.passportCap} />
          <div className="space-y-1.5">
            <div className="flex justify-between text-sm">
              <span className="text-text-muted">Rapor export (bu ay)</span>
              <span className="font-medium text-white">
                {u.reportExportsUsed} / {u.reportExportsCap}
              </span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-emerald-500/70"
                style={{
                  width: `${Math.min(100, Math.round((u.reportExportsUsed / u.reportExportsCap) * 100))}%`,
                }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl pv-card p-6 space-y-3">
          <div className="text-sm font-semibold text-white">Mevcut plan</div>
          <div className="text-lg font-semibold text-emerald-200">{subscription.plan_name}</div>
          <p className="text-sm text-text-muted">
            Faturalama: <span className="text-white">{subscription.billing_cycle}</span>
          </p>
          <p className="text-sm text-text-muted">
            Sonraki yenileme: <span className="text-white">{subscription.next_renewal}</span>
          </p>
          <p className="text-sm text-text-muted">
            Durum: <span className="text-emerald-300">{subscription.status}</span>
          </p>
        </div>

        <div className="rounded-2xl pv-card p-6 space-y-4">
          <div className="text-sm font-semibold text-white">Ekip koltukları</div>
          <div className="text-3xl font-bold text-white">
            {subscription.seats_used}{" "}
            <span className="text-lg font-normal text-text-muted">/ {subscription.seats_limit}</span>
          </div>
          <p className="text-sm text-text-muted">
            Yeni antrenör veya analist eklemek için plan yükseltmesi veya koltuk ekleme talebinde
            bulunabilirsiniz.
          </p>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => onPortalClick?.()}
              className="rounded-xl border border-white/15 bg-white/5 px-4 py-2 text-sm text-white hover:bg-white/10"
            >
              Fatura portalı (yakında)
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <Link
          href="/pricing"
          className="inline-flex items-center justify-center rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-500"
        >
          Planları incele
        </Link>
        <Link
          href="/demo-request"
          className="inline-flex items-center justify-center rounded-xl border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-semibold text-white hover:bg-white/10"
        >
          Demo talep et
        </Link>
      </div>
    </div>
  );
}
