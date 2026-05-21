"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiGetReport, apiGetAnalysis, apiGetAlerts, type MatchReport } from "@/lib/api";
import { useMatch } from "@/hooks/useMatches";
import { EmptyState } from "@/components/ui/EmptyState";

export default function MatchReportPage() {
  const params = useParams();
  const matchId = Number(params.id);
  
  const { data: match, loading: matchLoading } = useMatch(matchId);
  const [report, setReport] = useState<MatchReport | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch report
        const reportResult = await apiGetReport(matchId);
        if (reportResult.ok) {
          setReport(reportResult.data);
        }
        
        // Fetch analysis
        const analysisResult = await apiGetAnalysis(matchId);
        if (analysisResult.ok) {
          setAnalysis(analysisResult.data);
        }
        
        // Fetch alerts
        const alertsResult = await apiGetAlerts(matchId);
        if (alertsResult.ok) {
          setAlerts(alertsResult.data);
        }
        
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Rapor yüklenemedi");
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [matchId]);

  if (loading || matchLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-10 rounded-xl bg-white/5 w-64" />
        {[...Array(3)].map((_, i) => <div key={i} className="h-24 rounded-2xl bg-white/5" />)}
      </div>
    );
  }

  // Generate mock report if not found (for demo purposes)
  const displayReport = report || {
    id: 0,
    match_id: matchId,
    match_summary: analysis ? `${match?.opponentName || 'Rakip'} ile oynanan maç analiz edilmiştir. Takım ${analysis.possession_home?.toFixed(1)}% top hakimiyeti ile oynadı. Toplam ${analysis.passes_completed_home} pas tamamlandı ve ${analysis.shots_home} şut yapıldı.` : "Rapor henüz oluşturulmamış.",
    key_findings: analysis ? JSON.stringify([
      `Possession: ${analysis.possession_home?.toFixed(1)}% - Takım top hakimiyetinde ${analysis.possession_home > 50 ? 'üstün' : 'zayıf'} performans gösterdi`,
      `Pas Doğruluğu: ${analysis.passes_completed_home} tamamlanan pas - Ortalama pas başarısı iyi seviyede`,
      `Şut Başarısı: ${analysis.shots_home} şut - Hücum organizasyonu geliştirilebilir`
    ]) : "[]",
    tactical_recommendations: JSON.stringify([
      "Savunma organizasyonunu güçlendirmek için blok mesafelerini azaltın",
      "Geçiş oyununda hız artırarak kontra atakları daha etkili hale getirin",
      "Orta saha kontrolünü iyileştirmek için pas oyununu daha kısa tutun"
    ]),
    next_match_focus: JSON.stringify([
      "Savunma-orta saha mesafesi: < 20m hedefleyin",
      "Geçiş hızı: ≥ 5.1 m/s ortalama hedefleyin",
      "Pas başarısı: %80+ oranını koruyun"
    ]),
    status: "completed",
    generated_by: "ai_mock",
    created_at: new Date().toISOString(),
    disclaimer: "Bu rapor otomatik analiz adayıdır. Nihai değerlendirme antrenör gözlemiyle birlikte yapılmalıdır."
  };

  if (error && !report) {
    return (
      <EmptyState
        title="Rapor bulunamadı"
        description={error || "Bu maç için henüz rapor oluşturulmamış. Analiz tamamlandıktan sonra rapor otomatik olarak oluşturulacaktır."}
        icon="📄"
        action={
          <Link
            href={`/matches/${matchId}/analysis`}
            className="inline-flex rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
          >
            Analizi Gör
          </Link>
        }
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link href={`/matches/${matchId}/analysis`} className="text-sm text-emerald-400 hover:text-emerald-300 mb-2 inline-flex items-center gap-1">
            ← Video Analizi
          </Link>
          <h1 className="text-2xl font-bold text-white">Maç Raporu</h1>
          {match && (
            <p className="text-sm text-text-muted mt-1">
              {match.teamId ? `Team ${match.teamId}` : "Team"} vs {match.opponentName} • {new Date(match.matchDate).toLocaleDateString("tr-TR")}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <button className="rounded-xl bg-white/5 border border-white/10 px-4 py-2 text-sm font-semibold text-text-muted hover:text-white transition-all">
            📥 PDF İndir
          </button>
          <button className="rounded-xl bg-white/5 border border-white/10 px-4 py-2 text-sm font-semibold text-text-muted hover:text-white transition-all">
            🔗 Paylaş
          </button>
        </div>
      </div>

      {/* Report Status */}
      {displayReport.status !== "completed" && (
        <div className="rounded-xl bg-yellow-500/10 border border-yellow-500/30 p-4">
          <p className="text-sm text-yellow-200">
            ⏳ Rapor {displayReport.status === "generating" ? "oluşturuluyor..." : "hazırlanıyor..."}
          </p>
        </div>
      )}

      {/* Main Report */}
      <div className="pv-card rounded-2xl p-6 space-y-6">
        {/* Match Summary */}
        <section>
          <h2 className="text-lg font-semibold text-white mb-3">Maç Özeti</h2>
          <p className="text-sm text-text-muted leading-relaxed">
            {displayReport.match_summary || "Rapor henüz oluşturulmamış."}
          </p>
        </section>

        {/* Key Findings */}
        {displayReport.key_findings && (
          <section>
            <h2 className="text-lg font-semibold text-white mb-3">En Önemli Bulgular</h2>
            <ol className="space-y-2">
              {(() => {
                try {
                  const findings = typeof displayReport.key_findings === 'string' 
                    ? JSON.parse(displayReport.key_findings) 
                    : displayReport.key_findings;
                  return findings.map((finding: string, i: number) => (
                    <li key={i} className="text-sm text-text-muted flex gap-3">
                      <span className="text-emerald-400 font-semibold flex-shrink-0">{i + 1}.</span>
                      <span>{finding}</span>
                    </li>
                  ));
                } catch {
                  return <li className="text-sm text-text-muted">Bulgular yüklenemedi</li>;
                }
              })()}
            </ol>
          </section>
        )}

        {/* Analysis Metrics */}
        {analysis && (
          <section>
            <h2 className="text-lg font-semibold text-white mb-3">Takım Şekli Metrikleri</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="rounded-xl bg-white/5 border border-white/10 p-3">
                <div className="text-xs text-text-muted">Possession</div>
                <div className="text-lg font-bold text-emerald-400 mt-1">
                  {analysis.possession_home?.toFixed(1)}%
                </div>
              </div>
              <div className="rounded-xl bg-white/5 border border-white/10 p-3">
                <div className="text-xs text-text-muted">Passes</div>
                <div className="text-lg font-bold text-emerald-400 mt-1">
                  {analysis.passes_completed_home}
                </div>
              </div>
              <div className="rounded-xl bg-white/5 border border-white/10 p-3">
                <div className="text-xs text-text-muted">Shots</div>
                <div className="text-lg font-bold text-emerald-400 mt-1">
                  {analysis.shots_home}
                </div>
              </div>
              <div className="rounded-xl bg-white/5 border border-white/10 p-3">
                <div className="text-xs text-text-muted">Alerts</div>
                <div className="text-lg font-bold text-emerald-400 mt-1">
                  {alerts.length}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Tactical Recommendations */}
        {displayReport.tactical_recommendations && (
          <section>
            <h2 className="text-lg font-semibold text-white mb-3">Taktiksel Öneriler</h2>
            <ul className="space-y-2">
              {(() => {
                try {
                  const recs = typeof displayReport.tactical_recommendations === 'string' 
                    ? JSON.parse(displayReport.tactical_recommendations) 
                    : displayReport.tactical_recommendations;
                  return recs.map((rec: string, i: number) => (
                    <li key={i} className="text-sm text-text-muted flex gap-3">
                      <span className="text-emerald-400 flex-shrink-0">→</span>
                      <span>{rec}</span>
                    </li>
                  ));
                } catch {
                  return <li className="text-sm text-text-muted">Öneriler yüklenemedi</li>;
                }
              })()}
            </ul>
          </section>
        )}

        {/* Next Match Focus */}
        {displayReport.next_match_focus && (
          <section>
            <h2 className="text-lg font-semibold text-white mb-3">Bir Sonraki Maçta Takip Edilecek Göstergeler</h2>
            <ul className="space-y-2">
              {(() => {
                try {
                  const focus = typeof displayReport.next_match_focus === 'string' 
                    ? JSON.parse(displayReport.next_match_focus) 
                    : displayReport.next_match_focus;
                  return focus.map((f: string, i: number) => (
                    <li key={i} className="text-sm text-text-muted flex gap-3">
                      <span className="text-emerald-400 flex-shrink-0">→</span>
                      <span>{f}</span>
                    </li>
                  ));
                } catch {
                  return <li className="text-sm text-text-muted">Göstergeler yüklenemedi</li>;
                }
              })()}
            </ul>
          </section>
        )}

        {/* Disclaimer */}
        <div className="border-t border-white/10 pt-4">
          <p className="text-xs text-text-muted italic">
            ⚠️ {displayReport.disclaimer}
          </p>
        </div>
      </div>
    </div>
  );
}
