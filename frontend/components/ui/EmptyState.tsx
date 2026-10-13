"use client";

import React from "react";

export function EmptyState({
  title = "Henüz içerik yok",
  description = "Demo verileri yüklenene kadar bekleyin.",
  icon = "📂",
  action,
  secondaryAction,
}: {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  secondaryAction?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl pv-card px-8 py-14 text-center border border-white/5 bg-white/[0.02]">
      <div className="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center text-3xl mb-2">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-white">{title}</h3>
      <p className="max-w-md text-sm text-text-muted leading-relaxed">{description}</p>
      
      {(action || secondaryAction) && (
        <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
          {action}
          {secondaryAction}
        </div>
      )}
    </div>
  );
}

