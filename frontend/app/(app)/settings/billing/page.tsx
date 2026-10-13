"use client";

import Link from "next/link";
import React, { useCallback, useEffect, useState } from "react";

import { BillingPanel } from "@/components/settings/BillingPanel";
import { apiGetSubscription, type SubscriptionDto } from "@/lib/api";

export default function SettingsBillingRoutePage() {
  const [subscription, setSubscription] = useState<SubscriptionDto | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    window.setTimeout(() => setToast(null), 3200);
  }, []);

  useEffect(() => {
    void apiGetSubscription().then(setSubscription);
  }, []);

  return (
    <div className="space-y-6">
      {toast ? (
        <div className="fixed bottom-6 right-6 z-40 rounded-xl border border-emerald-500/30 bg-emerald-950/90 px-4 py-3 text-sm text-emerald-100 shadow-lg">
          {toast}
        </div>
      ) : null}

      <div>
        <Link
          href="/settings"
          className="text-sm font-medium text-emerald-200/80 hover:text-emerald-100"
        >
          ← Tüm ayarlara dön
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-white">Abonelik ve faturalama</h1>
        <p className="mt-2 max-w-2xl text-sm text-text-muted">
          Kullanım özetiniz aşağıdadır. Plan değişikliği veya ek koltuk için önce demo görüşmesi
          öneriyoruz; böylece sahadaki ihtiyacınıza göre doğru paket seçilir.
        </p>
      </div>

      {!subscription ? (
        <div className="rounded-2xl pv-card p-8 text-center text-sm text-text-muted">Yükleniyor…</div>
      ) : (
        <BillingPanel
          subscription={subscription}
          onPortalClick={() => showToast("Fatura portalı yakında aktif olacak.")}
        />
      )}
    </div>
  );
}
