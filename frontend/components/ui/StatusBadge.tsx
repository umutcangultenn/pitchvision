"use client";

import React from "react";

export function StatusBadge({
  status,
}: {
  status: string;
}) {
  const tone =
    status === "completed"
      ? "bg-success/15 text-success border-success/30"
      : status === "processing"
      ? "bg-warning/15 text-warning border-warning/30"
      : status === "cancelled" || status === "failed" || status === "error"
      ? "bg-danger/15 text-danger border-danger/30"
      : "bg-white/5 text-text border-white/10";

  const label =
    status === "completed"
      ? "Tamamlandı"
      : status === "processing"
      ? "İşleniyor"
      : status === "cancelled"
      ? "İptal Edildi"
      : status === "failed" || status === "error"
      ? "Hata"
      : status === "scheduled"
      ? "Planlandı"
      : status === "live"
      ? "Canlı"
      : status;

  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${tone}`}>
      {label}
    </span>
  );
}

