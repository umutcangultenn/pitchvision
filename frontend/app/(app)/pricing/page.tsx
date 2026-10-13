"use client";

import Link from "next/link";
import React from "react";

import { PlanCard } from "@/components/pricing/PlanCard";
import { PRICING_PLANS } from "@/lib/pricing";

export default function PricingPage() {
  return (
    <div className="space-y-8">
      <div className="max-w-3xl">
        <div className="text-sm font-medium text-emerald-200/80">Planlar</div>
        <h1 className="mt-1 text-2xl font-semibold text-white md:text-3xl">
          Kulübünüze uygun PitchVision Lite paketi
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-text-muted md:text-base">
          Maç analizi, oyuncu gelişimi ve scouting araçlarını tek çatı altında topluyoruz. Aşağıdaki
          planlar yönlendirme amaçlıdır; kesin teklif ve kurulum için kısa bir demo görüşmesi en doğru
          adımdır. Antrenör ve yönetici ekipleri için sözleşme dili yerine saha dilinde özetledik.
        </p>
      </div>

      <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-sm text-emerald-100/90">
        <strong className="text-white">Nasıl ilerleriz?</strong>{" "}
        Demo Talep Et ile formu doldurun; ekibimiz yaş kategorilerinize ve hedeflerinize göre
        örnek akış gösterir. Planı Seç, aynı formu ilgilendiğiniz paketle önceden işaretleyerek
        bize iletir — ödeme entegrasyonu açıldığında buradan tamamlanabilecek.
      </div>

      <div className="grid gap-5 lg:grid-cols-2 xl:grid-cols-4">
        {PRICING_PLANS.map((plan) => (
          <PlanCard key={plan.id} plan={plan} />
        ))}
      </div>

      <div className="flex flex-wrap gap-3 border-t border-white/10 pt-6">
        <Link
          href="/demo-request"
          className="inline-flex items-center justify-center rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-500"
        >
          Demo talep formuna git
        </Link>
        <Link
          href="/settings/billing"
          className="inline-flex items-center justify-center rounded-xl border border-white/15 bg-white/5 px-5 py-2.5 text-sm font-semibold text-white hover:bg-white/10"
        >
          Mevcut kullanımımı görüntüle
        </Link>
      </div>
    </div>
  );
}
