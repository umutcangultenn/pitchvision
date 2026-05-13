"use client";

import React, { useState } from "react";
import type { TacticalAlert } from "@/types/domain";
import { EmptyState } from "@/components/ui/EmptyState";

type AlertsTabProps = {
  alerts: TacticalAlert[];
  onShowInVideo?: (alertId: number, startTime: number) => void;
  onCreateClip?: (alertId: number) => void;
  onUpdateStatus?: (alertId: number, status: TacticalAlert["status"]) => void;
};

export function AlertsTab({ alerts, onShowInVideo, onCreateClip, onUpdateStatus }: AlertsTabProps) {
  const [filter, setFilter] = useState<"all" | "open" | "in_review" | "resolved">("all");

  const filteredAlerts = alerts.filter(alert => 
    filter === "all" || alert.status === filter
  );

  const getSeverityColor = (severity: TacticalAlert["severity"]) => {
    switch (severity) {
      case "critical": return "text-danger border-danger/30 bg-danger/10";
      case "high": return "text-warning border-warning/30 bg-warning/10";
      case "medium": return "text-accent border-accent/30 bg-accent/10";
      case "low": return "text-success border-success/30 bg-success/10";
      default: return "text-text-muted border-white/10 bg-white/5";
    }
  };

  const getStatusColor = (status: TacticalAlert["status"]) => {
    switch (status) {
      case "open": return "text-danger";
      case "in_review": return "text-warning";
      case "resolved": return "text-success";
      case "dismissed": return "text-text-muted";
      default: return "text-text-muted";
    }
  };

  const getStatusLabel = (status: TacticalAlert["status"]) => {
    switch (status) {
      case "open": return "Açık";
      case "in_review": return "İnceleniyor";
      case "resolved": return "Çözüldü";
      case "dismissed": return "Reddedildi";
      default: return status;
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold text-white">Taktiksel Uyarılar</div>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value as any)}
          className="px-3 py-1.5 rounded-lg text-xs bg-white/10 border border-white/20 text-text"
        >
          <option value="all">Tümü ({alerts.length})</option>
          <option value="open">Açık ({alerts.filter(a => a.status === "open").length})</option>
          <option value="in_review">İnceleniyor ({alerts.filter(a => a.status === "in_review").length})</option>
          <option value="resolved">Çözüldü ({alerts.filter(a => a.status === "resolved").length})</option>
        </select>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {filteredAlerts.map(alert => (
          <div
            key={alert.id}
            className={`p-4 rounded-lg border transition-all ${getSeverityColor(alert.severity)}`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <div className="text-sm font-medium text-white">{alert.title}</div>
                  <div className="text-xs px-2 py-1 rounded bg-black/20">
                    {formatTime(alert.startTime)}
                  </div>
                </div>
                <div className="text-xs text-text-muted mb-2">{alert.description}</div>
                <div className="flex items-center gap-3 text-xs">
                  <span>Güven: {Math.round((alert.confidence || 0) * 100)}%</span>
                  <span className={getStatusColor(alert.status)}>
                    {getStatusLabel(alert.status)}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => onShowInVideo?.(alert.id, alert.startTime)}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all"
              >
                🎬 Videoda Göster
              </button>
              
              <button
                onClick={() => onCreateClip?.(alert.id)}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-warning/20 border border-warning/40 text-warning hover:bg-warning/30 transition-all"
              >
                ✂️ Klip Oluştur
              </button>

              {alert.status === "open" && (
                <>
                  <button
                    onClick={() => onUpdateStatus?.(alert.id, "in_review")}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all"
                  >
                    👁️ İncele
                  </button>
                  <button
                    onClick={() => onUpdateStatus?.(alert.id, "resolved")}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-success/20 border border-success/40 text-success hover:bg-success/30 transition-all"
                  >
                    ✅ Onayla
                  </button>
                  <button
                    onClick={() => onUpdateStatus?.(alert.id, "dismissed")}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-danger/20 border border-danger/40 text-danger hover:bg-danger/30 transition-all"
                  >
                    ❌ Reddet
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredAlerts.length === 0 && (
        <div className="py-8">
          <EmptyState
            title="Uyarı bulunamadı"
            description={filter === "all" ? "Bu maçta henüz taktiksel uyarı tespit edilmedi." : `"${getStatusLabel(filter)}" durumunda uyarı bulunmuyor.`}
            icon="⚠️"
          />
        </div>
      )}

      <div className="p-4 rounded-lg bg-warning/10 border border-warning/30">
        <div className="text-xs font-medium text-warning mb-2">⚠️ Önemli Uyarı</div>
        <div className="text-xs text-text-muted">
          Bu uyarılar otomatik analiz adayıdır. Nihai değerlendirme antrenör gözlemiyle birlikte yapılmalıdır.
        </div>
      </div>
    </div>
  );
}