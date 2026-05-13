"""
PDF export helper.
Generates a simple HTML string suitable for headless-browser PDF rendering.
No external PDF library required — the HTML can be printed via browser or
passed to tools like weasyprint / puppeteer.
"""
from typing import Any, Dict
from datetime import datetime


def _fmt_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def _severity_color(severity: str) -> str:
    return {
        "critical": "#ef4444",
        "high": "#f97316",
        "medium": "#eab308",
        "low": "#22c55e",
    }.get(severity, "#6b7280")


def render_report_html(report: Dict[str, Any]) -> str:
    """
    Raporu HTML string olarak render eder.
    PDF export için tarayıcıya veya weasyprint'e gönderilebilir.
    """
    ts = report.get("team_shape", {})
    alerts = report.get("alerts", [])
    clips = report.get("clips", [])
    players = report.get("players", [])
    drills = report.get("drill_recommendations", [])
    findings = report.get("top_findings", [])
    indicators = report.get("next_match_indicators", [])

    # ── Alerts HTML ────────────────────────────────────────────────────────────
    alerts_html = ""
    for a in alerts:
        color = _severity_color(a.get("severity", "low"))
        drill = a.get("drill")
        drill_html = ""
        if drill:
            drill_html = f"""
            <div class="drill-badge">
              🏋️ Önerilen Drill: <strong>{drill.get('title', '')}</strong>
              ({drill.get('duration_minutes', 0)} dk)
            </div>"""
        alerts_html += f"""
        <div class="alert-card">
          <div class="alert-header">
            <span class="severity-dot" style="background:{color}"></span>
            <strong>{a.get('title', '')}</strong>
            <span class="time-badge">{_fmt_time(a.get('timestamp_seconds', 0))}</span>
            <span class="confidence">%{int(a.get('confidence', 0) * 100)} güven</span>
          </div>
          <p class="alert-desc">{a.get('description', '')}</p>
          {drill_html}
        </div>"""

    # ── Clips HTML ─────────────────────────────────────────────────────────────
    clips_html = ""
    for c in clips:
        clips_html += f"""
        <div class="clip-row">
          <span class="clip-title">{c.get('title', '')}</span>
          <span class="clip-time">{_fmt_time(c.get('start_time', 0))} – {_fmt_time(c.get('end_time', 0))}</span>
          <span class="clip-tag">{c.get('tag', '')}</span>
        </div>"""

    # ── Players HTML ───────────────────────────────────────────────────────────
    players_html = ""
    for p in players:
        avg = (p.get("tactical_score", 0) + p.get("technical_score", 0) +
               p.get("physical_score", 0) + p.get("decision_score", 0)) / 4
        players_html += f"""
        <tr>
          <td>{p.get('name', '')}</td>
          <td>{p.get('position', '')}</td>
          <td>{p.get('minutes_played', 0)}'</td>
          <td>{p.get('tactical_score', 0):.1f}</td>
          <td>{p.get('technical_score', 0):.1f}</td>
          <td>{p.get('physical_score', 0):.1f}</td>
          <td>{p.get('decision_score', 0):.1f}</td>
          <td><strong>{avg:.1f}</strong></td>
          <td>{p.get('alerts_involved', 0)}</td>
        </tr>"""

    # ── Drills HTML ────────────────────────────────────────────────────────────
    drills_html = ""
    for d in drills:
        points = "".join(f"<li>{pt}</li>" for pt in d.get("coaching_points", []))
        drills_html += f"""
        <div class="drill-card">
          <h4>{d.get('title', '')}</h4>
          <p class="drill-trigger">Tetikleyen: {d.get('triggered_by_title', '')}</p>
          <p>{d.get('description', '')}</p>
          <p><strong>Süre:</strong> {d.get('duration_minutes', 0)} dk &nbsp;
             <strong>Odak:</strong> {', '.join(d.get('focus', []))}</p>
          <ul class="coaching-points">{points}</ul>
        </div>"""

    # ── Findings & Indicators ──────────────────────────────────────────────────
    findings_html = "".join(f"<li>{f}</li>" for f in findings)
    indicators_html = "".join(f"<li>{i}</li>" for i in indicators)

    score = f"{report.get('score_for', 0)}-{report.get('score_against', 0)}"
    generated = report.get("generated_at", datetime.now().isoformat())[:10]

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<title>Maç Raporu — {report.get('team_name', '')} vs {report.get('opponent_name', '')}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #1e293b; background: #fff; font-size: 13px; }}
  .page {{ max-width: 900px; margin: 0 auto; padding: 32px; }}
  h1 {{ font-size: 22px; color: #0f172a; }}
  h2 {{ font-size: 16px; color: #1e40af; margin: 24px 0 10px; border-bottom: 2px solid #e2e8f0; padding-bottom: 4px; }}
  h3 {{ font-size: 14px; color: #334155; margin: 16px 0 6px; }}
  h4 {{ font-size: 13px; color: #1e293b; margin-bottom: 4px; }}
  p {{ line-height: 1.6; color: #475569; }}
  .cover {{ background: #0f172a; color: #fff; padding: 32px; border-radius: 8px; margin-bottom: 24px; }}
  .cover h1 {{ color: #fff; font-size: 26px; }}
  .cover .meta {{ display: flex; gap: 24px; margin-top: 12px; font-size: 12px; color: #94a3b8; }}
  .cover .score {{ font-size: 36px; font-weight: 700; color: #38bdf8; margin-top: 8px; }}
  .metrics-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 12px 0; }}
  .metric-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; text-align: center; }}
  .metric-box .val {{ font-size: 20px; font-weight: 700; color: #1e40af; }}
  .metric-box .lbl {{ font-size: 11px; color: #64748b; margin-top: 2px; }}
  .alert-card {{ border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; margin-bottom: 10px; }}
  .alert-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }}
  .severity-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
  .time-badge {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 11px; }}
  .confidence {{ font-size: 11px; color: #64748b; margin-left: auto; }}
  .alert-desc {{ font-size: 12px; color: #64748b; }}
  .drill-badge {{ margin-top: 6px; font-size: 11px; background: #eff6ff; color: #1d4ed8; padding: 4px 8px; border-radius: 4px; display: inline-block; }}
  .clip-row {{ display: flex; gap: 12px; align-items: center; padding: 8px 0; border-bottom: 1px solid #f1f5f9; font-size: 12px; }}
  .clip-title {{ flex: 1; font-weight: 500; }}
  .clip-time {{ color: #64748b; }}
  .clip-tag {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 11px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  th {{ background: #f8fafc; padding: 8px; text-align: left; border-bottom: 2px solid #e2e8f0; font-size: 11px; color: #64748b; }}
  td {{ padding: 8px; border-bottom: 1px solid #f1f5f9; }}
  .drill-card {{ border: 1px solid #dbeafe; border-radius: 6px; padding: 14px; margin-bottom: 12px; background: #f0f9ff; }}
  .drill-trigger {{ font-size: 11px; color: #3b82f6; margin-bottom: 6px; }}
  .coaching-points {{ margin-top: 8px; padding-left: 18px; }}
  .coaching-points li {{ font-size: 12px; color: #475569; margin-bottom: 3px; }}
  ul.findings {{ padding-left: 18px; }}
  ul.findings li {{ margin-bottom: 6px; line-height: 1.5; }}
  .disclaimer {{ background: #fefce8; border: 1px solid #fde047; border-radius: 6px; padding: 12px; margin-top: 24px; font-size: 12px; color: #713f12; }}
  @media print {{ .page {{ padding: 16px; }} }}
</style>
</head>
<body>
<div class="page">

  <!-- 1. Kapak -->
  <div class="cover">
    <h1>Maç Analiz Raporu</h1>
    <div class="meta">
      <span>📅 {report.get('match_date', '')[:10]}</span>
      <span>🏷️ {report.get('age_category', '')}</span>
      <span>📹 {report.get('video_source', '')}</span>
      <span>🎯 Kalibrasyon: {report.get('calibration_quality', '')}</span>
      <span>📊 Tracking: %{int(report.get('tracking_confidence', 0) * 100)}</span>
    </div>
    <div class="score">{report.get('team_name', '')} {score} {report.get('opponent_name', '')}</div>
    <div style="font-size:11px;color:#94a3b8;margin-top:8px;">Oluşturulma: {generated}</div>
  </div>

  <!-- 2. Maç Özeti -->
  <h2>Maç Özeti</h2>
  <p>{report.get('summary', '')}</p>

  <!-- 3. En Önemli 3 Bulgu -->
  <h2>En Önemli Bulgular</h2>
  <ul class="findings">{findings_html}</ul>

  <!-- 4. Takım Şekli Metrikleri -->
  <h2>Takım Şekli Metrikleri</h2>
  <div class="metrics-grid">
    <div class="metric-box"><div class="val">{ts.get('team_length', 0):.1f}m</div><div class="lbl">Takım Boyu</div></div>
    <div class="metric-box"><div class="val">{ts.get('team_width', 0):.1f}m</div><div class="lbl">Takım Genişliği</div></div>
    <div class="metric-box"><div class="val">{ts.get('compactness', 0):.1f}m</div><div class="lbl">Kompaktlık</div></div>
    <div class="metric-box"><div class="val">{ts.get('defense_midfield_gap', 0):.1f}m</div><div class="lbl">Sav-Orta Mesafe</div></div>
    <div class="metric-box"><div class="val">{ts.get('midfield_forward_gap', 0):.1f}m</div><div class="lbl">Orta-Forvet Mesafe</div></div>
    <div class="metric-box"><div class="val">{ts.get('transition_speed', 0):.1f} m/s</div><div class="lbl">Geçiş Hızı</div></div>
  </div>

  <!-- 5. Taktiksel Uyarılar -->
  <h2>Taktiksel Uyarılar ({len(alerts)} adet)</h2>
  {alerts_html if alerts_html else '<p style="color:#94a3b8">Uyarı bulunamadı.</p>'}

  <!-- 6. Klipler -->
  <h2>Klipler ({len(clips)} adet)</h2>
  {clips_html if clips_html else '<p style="color:#94a3b8">Klip bulunamadı.</p>'}

  <!-- 7. Oyuncu Performansı -->
  <h2>Oyuncu Performansı</h2>
  <table>
    <thead>
      <tr>
        <th>Oyuncu</th><th>Pos.</th><th>Süre</th>
        <th>Taktik</th><th>Teknik</th><th>Fizik</th><th>Karar</th>
        <th>Ort.</th><th>Uyarı</th>
      </tr>
    </thead>
    <tbody>{players_html}</tbody>
  </table>

  <!-- 8. Antrenman Önerileri -->
  <h2>Antrenman Önerileri</h2>
  {drills_html if drills_html else '<p style="color:#94a3b8">Öneri bulunamadı.</p>'}

  <!-- 9. Bir Sonraki Maçta Takip Edilecek Göstergeler -->
  <h2>Bir Sonraki Maçta Takip Edilecek Göstergeler</h2>
  <ul class="findings">{indicators_html}</ul>

  <!-- Etik Not -->
  <div class="disclaimer">
    ⚠️ {report.get('disclaimer', '')}
  </div>

</div>
</body>
</html>"""
