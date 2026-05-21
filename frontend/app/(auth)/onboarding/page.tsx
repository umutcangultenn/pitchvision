"use client";

import React from "react";
import { useRouter } from "next/navigation";

import Link from "next/link";

import { ProcessingStep, type ProcessingStepItem } from "@/components/ui/ProcessingStep";

export default function OnboardingPage() {
  const router = useRouter();

  const steps: ProcessingStepItem[] = [
    { key: "org", icon: "🏟️", label: "Kulüp & Sezon", status: "completed", description: "Demo verileri hazır." },
    { key: "upload", icon: "📤", label: "Maç Yükle", status: "current", description: "Video analizi için yükleme." },
    { key: "analyze", icon: "📊", label: "Analiz", status: "pending", description: "Taktik raporlar ve paslar." },
    { key: "plan", icon: "🏃", label: "Antrenman", status: "pending", description: "Önerilen drill'ler." },
  ];

  return (
    <main className="mx-auto max-w-5xl px-4 py-10">
      <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="text-sm font-medium text-emerald-200/80">PitchVision Lite</div>
          <h1 className="mt-2 text-2xl font-semibold text-white">İlk kurulum</h1>
          <p className="mt-2 max-w-xl text-sm text-text-muted">
            MVP demo akışını kullanın: maçı yükleyin, işlenmesini bekleyin ve raporu inceleyin.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-text-muted hover:text-white hover:border-emerald-400/30"
          >
            Atlansın
          </Link>
          <button
            onClick={() => router.push("/dashboard")}
            className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500"
          >
            Devam et
          </button>
        </div>
      </div>

      <div className="mt-8">
        <ProcessingStep steps={steps} />
      </div>
    </main>
  );
}
