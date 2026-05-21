"use client";

import React, { useEffect } from "react";

export type ToastItem = {
  id: string;
  title: string;
  message?: string;
  tone?: "success" | "danger" | "info" | "warning";
};

export function Toast({
  toasts,
  onDismiss,
}: {
  toasts: ToastItem[];
  onDismiss: (id: string) => void;
}) {
  useEffect(() => {
    for (const t of toasts) {
      const timer = window.setTimeout(() => onDismiss(t.id), 4500);
      return () => window.clearTimeout(timer);
    }
  }, [toasts, onDismiss]);

  if (!toasts.length) return null;

  return (
    <div className="fixed right-4 top-4 z-50 flex w-full max-w-sm flex-col gap-3">
      {toasts.map((t) => {
        const tone =
          t.tone === "success"
            ? "border-success/30 bg-success/10 text-success"
            : t.tone === "danger"
            ? "border-danger/30 bg-danger/10 text-danger"
            : t.tone === "warning"
            ? "border-warning/30 bg-warning/10 text-warning"
            : "border-accent/30 bg-accent/10 text-accent";
        return (
          <div key={t.id} className={`rounded-xl pv-surface pv-ring border ${tone} px-4 py-3`}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-sm font-semibold">{t.title}</div>
                {t.message ? <div className="mt-1 text-sm text-text-muted">{t.message}</div> : null}
              </div>
              <button
                onClick={() => onDismiss(t.id)}
                className="rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-xs text-text-muted hover:text-white"
              >
                Kapat
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Backward-compat / naming convenience
export const ToastStack = Toast;

