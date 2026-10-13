"use client";

import React from "react";

export type StepStatus = "completed" | "current" | "pending" | "error";

export type ProcessingStepItem = {
  key: string;
  icon: string;
  label: string;
  description: string;
  status: StepStatus;
};

function StepIcon({ status, icon }: { status: StepStatus; icon: string }) {
  const base = "h-10 w-10 rounded-full flex items-center justify-center text-lg flex-shrink-0 transition-all";
  if (status === "completed")
    return (
      <div className={`${base} bg-success/20 border border-success/40`}>
        <span className="text-success text-base">✓</span>
      </div>
    );
  if (status === "current")
    return (
      <div className={`${base} bg-accent/20 border border-accent/60 ring-2 ring-accent/30 animate-pulse`}>
        <div className="relative">
          <span className="animate-spin text-accent">⟳</span>
          <div className="absolute inset-0 rounded-full bg-accent/20 animate-ping"></div>
        </div>
      </div>
    );
  if (status === "error")
    return (
      <div className={`${base} bg-danger/20 border border-danger/50`}>
        <span className="text-danger text-base">✕</span>
      </div>
    );
  return (
    <div className={`${base} bg-white/5 border border-white/10`}>
      <span className="opacity-40">{icon}</span>
    </div>
  );
}

function StepLabel({ status }: { status: StepStatus }) {
  if (status === "completed") return <span className="text-xs font-medium text-success">Tamamlandı</span>;
  if (status === "current") return <span className="text-xs font-medium text-accent animate-pulse">İşleniyor…</span>;
  if (status === "error") return <span className="text-xs font-medium text-danger">Hata</span>;
  return <span className="text-xs text-text-soft">Bekliyor</span>;
}

export function ProcessingStep({ steps }: { steps: ProcessingStepItem[] }) {
  const currentIdx = steps.findIndex((s) => s.status === "current");
  const completedCount = steps.filter((s) => s.status === "completed").length;
  const progress = Math.round((completedCount / steps.length) * 100);

  return (
    <div className="space-y-4">
      {/* Progress bar */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-2 rounded-full bg-white/10 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-1000 ease-out ${
              steps.some(s => s.status === "error") 
                ? "bg-gradient-to-r from-danger to-danger/80" 
                : "bg-gradient-to-r from-accent to-accent-2"
            }`}
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="text-xs text-text-muted tabular-nums w-12 text-right">
          {steps.some(s => s.status === "error") ? "Hata" : `${progress}%`}
        </span>
      </div>

      {/* Steps */}
      <div className="space-y-1">
        {steps.map((step, idx) => {
          const isLast = idx === steps.length - 1;
          const labelColor =
            step.status === "completed"
              ? "text-text"
              : step.status === "current"
              ? "text-white font-semibold"
              : step.status === "error"
              ? "text-danger"
              : "text-text-soft";

          return (
            <div key={step.key} className="flex gap-3">
              {/* Left: icon + connector */}
              <div className="flex flex-col items-center">
                <StepIcon status={step.status} icon={step.icon} />
                {!isLast && (
                  <div
                    className={`w-px flex-1 mt-1 min-h-[1.5rem] ${
                      step.status === "completed" ? "bg-success/30" : "bg-white/10"
                    }`}
                  />
                )}
              </div>

              {/* Right: content */}
              <div className={`pb-4 ${isLast ? "" : ""}`}>
                <div className="flex items-center gap-2 mt-2">
                  <span className={`text-sm ${labelColor}`}>{step.label}</span>
                  <StepLabel status={step.status} />
                </div>
                <p className="text-xs text-text-soft mt-0.5 leading-relaxed">{step.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
