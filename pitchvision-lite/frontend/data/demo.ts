/**
 * Anadolu Akademi — demo / mock data
 * Backend seed (app/db/seed.py) ile birebir tutarlı.
 */
import type {
  AlertStatus,
  AlertType,
  DrillDifficulty,
  DrillRecommendation,
  Match,
  MatchStatus,
  MetricType,
  Organization,
  OrganizationType,
  Player,
  PitchSize,
  ProblemType,
  Report,
  ReportType,
  ScoutNote,
  Severity,
  Team,
  VideoAsset,
  VideoAssetStatus,
  VideoSource,
} from "@/types/domain";

// ── Sabit zaman damgaları ─────────────────────────────────────────────────────
const NOW = "2026-05-14T06:00:00.000Z";

// ── Organization ──────────────────────────────────────────────────────────────
export const mockOrganizations: Organization[] = [
  {
    id: 1,
    name: "Anadolu Akademi",
    city: "İstanbul",
    logoUrl: undefined,
    organizationType: "academy" satisfies OrganizationType,
    createdAt: NOW,
  },
];

// ── Teams ─────────────────────────────────────────────────────────────────────
export const mockTeams: Team[] = [
  { id: 1, organizationId: 1, name: "U15 Kırmızı Takım", ageCategory: "U15", gameFormat: "11v11", defaultFormation: "4-3-3",   pitchLength: 105, pitchWidth: 68, season: "2025/26", createdAt: NOW },
  { id: 2, organizationId: 1, name: "U13 Akademi",        ageCategory: "U13", gameFormat: "11v11", defaultFormation: "4-4-2",   pitchLength: 105, pitchWidth: 68, season: "2025/26", createdAt: NOW },
  { id: 3, organizationId: 1, name: "U17 Gelişim",        ageCategory: "U17", gameFormat: "11v11", defaultFormation: "4-2-3-1", pitchLength: 105, pitchWidth: 68, season: "2025/26", createdAt: NOW },
  { id: 4, organizationId: 1, name: "U11 Futbol Okulu",   ageCategory: "U11", gameFormat: "7v7",   defaultFormation: "3-3-1",   pitchLength:  68, pitchWidth: 50, season: "2025/26", createdAt: NOW },
];


// ── Players ───────────────────────────────────────────────────────────────────
export const mockPlayers: Player[] = [
  // U15 Kırmızı Takım
  { id: 1, organizationId: 1, teamId: 1, firstName: "Arda",  lastName: "Yılmaz", birthDate: "2011-03-14", position: "CM",  dominantFoot: "right", heightCm: 168, weightKg: 58, technicalScore: 7.4, tacticalScore: 7.1, physicalScore: 6.8, decisionScore: 7.0, developmentVelocity: 0.52, createdAt: NOW },
  { id: 2, organizationId: 1, teamId: 1, firstName: "Emir",  lastName: "Kaya",   birthDate: "2011-07-22", position: "CB",  dominantFoot: "right", heightCm: 176, weightKg: 68, technicalScore: 6.5, tacticalScore: 7.6, physicalScore: 7.2, decisionScore: 7.0, developmentVelocity: 0.45, createdAt: NOW },
  { id: 3, organizationId: 1, teamId: 1, firstName: "Kerem", lastName: "Demir",  birthDate: "2010-11-05", position: "RW",  dominantFoot: "right", heightCm: 170, weightKg: 60, technicalScore: 7.8, tacticalScore: 7.0, physicalScore: 7.1, decisionScore: 7.3, developmentVelocity: 0.61, createdAt: NOW },
  { id: 4, organizationId: 1, teamId: 1, firstName: "Can",   lastName: "Öztürk", birthDate: "2011-09-11", position: "GK",  dominantFoot: "right", heightCm: 178, weightKg: 70, technicalScore: 6.0, tacticalScore: 7.2, physicalScore: 7.0, decisionScore: 7.4, developmentVelocity: 0.44, createdAt: NOW },
  // U13 Akademi
  { id: 5, organizationId: 1, teamId: 2, firstName: "Efe",   lastName: "Arslan", birthDate: "2013-05-30", position: "LB",  dominantFoot: "left",  heightCm: 162, weightKg: 52, technicalScore: 6.2, tacticalScore: 6.8, physicalScore: 6.5, decisionScore: 6.4, developmentVelocity: 0.38, createdAt: NOW },
  // U17 Gelişim
  { id: 6, organizationId: 1, teamId: 3, firstName: "Mert",  lastName: "Şahin",  birthDate: "2009-02-18", position: "ST",  dominantFoot: "right", heightCm: 180, weightKg: 72, technicalScore: 7.2, tacticalScore: 6.9, physicalScore: 7.5, decisionScore: 7.1, developmentVelocity: 0.58, createdAt: NOW },
];

// ── Matches ───────────────────────────────────────────────────────────────────
export const mockMatches: Match[] = [
  { id: 1001, organizationId: 1, teamId: 1, opponentName: "Mavi Spor",     matchDate: "2026-04-12T13:00:00.000Z", ageCategory: "U15", gameFormat: "11v11", pitchLength: 105, pitchWidth: 68, firstHalfAttackDirection: "left_to_right",  scoreFor: 3, scoreAgainst: 1, videoSource: "file_upload" satisfies VideoSource, status: "completed"  satisfies MatchStatus, createdAt: NOW },
  { id: 1002, organizationId: 1, teamId: 2, opponentName: "Kartal Akademi", matchDate: "2026-04-19T11:00:00.000Z", ageCategory: "U13", gameFormat: "11v11", pitchLength: 105, pitchWidth: 68, firstHalfAttackDirection: "right_to_left", scoreFor: 2, scoreAgainst: 2, videoSource: "file_upload" satisfies VideoSource, status: "completed"  satisfies MatchStatus, createdAt: NOW },
  { id: 1003, organizationId: 1, teamId: 3, opponentName: "Anadolu FK",     matchDate: "2026-04-26T14:00:00.000Z", ageCategory: "U17", gameFormat: "11v11", pitchLength: 105, pitchWidth: 68, firstHalfAttackDirection: "left_to_right",  scoreFor: 1, scoreAgainst: 0, videoSource: "file_upload" satisfies VideoSource, status: "processing" satisfies MatchStatus, createdAt: NOW },
  { id: 1004, organizationId: 1, teamId: 4, opponentName: "Kuzey Gençlik",  matchDate: "2026-05-03T10:00:00.000Z", ageCategory: "U11", gameFormat: "7v7",   pitchLength:  68, pitchWidth: 50, firstHalfAttackDirection: "left_to_right",  scoreFor: 4, scoreAgainst: 2, videoSource: "file_upload" satisfies VideoSource, status: "completed"  satisfies MatchStatus, createdAt: NOW },
];

// ── VideoAssets ───────────────────────────────────────────────────────────────
export const mockVideos: VideoAsset[] = [
  { id: 5001, matchId: 1001, fileName: "u15_mavi_spor.mp4",      storagePath: "org/1/matches/1001/u15_mavi_spor.mp4",      durationSeconds: 5400, width: 1920, height: 1080, fps: 25, status: "ready"      satisfies VideoAssetStatus, createdAt: NOW },
  { id: 5002, matchId: 1002, fileName: "u13_kartal_akademi.mp4", storagePath: "org/1/matches/1002/u13_kartal_akademi.mp4", durationSeconds: 5220, width: 1920, height: 1080, fps: 25, status: "ready"      satisfies VideoAssetStatus, createdAt: NOW },
  { id: 5003, matchId: 1003, fileName: "u17_anadolu_fk.mp4",     storagePath: "org/1/matches/1003/u17_anadolu_fk.mp4",     durationSeconds: undefined,  width: 1920, height: 1080, fps: 25, status: "processing" satisfies VideoAssetStatus, createdAt: NOW },
  { id: 5004, matchId: 1004, fileName: "u11_kuzey_genclik.mp4",  storagePath: "org/1/matches/1004/u11_kuzey_genclik.mp4",  durationSeconds: 3600, width: 1920, height: 1080, fps: 25, status: "ready"      satisfies VideoAssetStatus, createdAt: NOW },
];


// ── TacticalAlerts ────────────────────────────────────────────────────────────
export const mockAlerts = [
  // U15 vs Mavi Spor
  { id: 3001, matchId: 1001, teamId: 1, playerId: 2, alertType: "defensive_line_break"   as AlertType, startTime:  450, endTime:  510, confidence: 0.82, severity: "high"     as Severity, status: "open"      as AlertStatus, title: "Savunma hattı bozulması",   description: "Savunma hattı senkronizasyonu bozuldu, rakip derin koşuya alan açıldı.",    relatedMetric: "defensive_line", suggestedClipId: 9003, createdAt: NOW },
  { id: 3002, matchId: 1001, teamId: 1, playerId: 1, alertType: "block_gap_wide"         as AlertType, startTime:  820, endTime:  880, confidence: 0.76, severity: "high"     as Severity, status: "in_review" as AlertStatus, title: "Bloklar arası kopukluk",    description: "Savunma ve orta saha bloğu arasında 28 m boşluk oluştu.",                   relatedMetric: "compactness",    suggestedClipId: undefined, createdAt: NOW },
  { id: 3003, matchId: 1001, teamId: 1, playerId: 1, alertType: "poor_transition_defense" as AlertType, startTime: 1200, endTime: 1260, confidence: 0.79, severity: "critical" as Severity, status: "open"      as AlertStatus, title: "Geçiş savunması zayıf",     description: "Top kaybı sonrası 5 saniyede geri dönüş sağlanamadı.",                      relatedMetric: "transition_speed", suggestedClipId: 9001, createdAt: NOW },
  { id: 3004, matchId: 1001, teamId: 1, playerId: 3, alertType: "depth_run_opportunity"  as AlertType, startTime: 1540, endTime: 1600, confidence: 0.87, severity: "medium"   as Severity, status: "resolved"  as AlertStatus, title: "Derin koşu fırsatı",         description: "Savunma hattı arkasında derin koşu için uygun zamanlama yakalandı.",        relatedMetric: "field_tilt",     suggestedClipId: 9002, createdAt: NOW },
  { id: 3005, matchId: 1001, teamId: 1, playerId: 1, alertType: "lack_of_support_run"    as AlertType, startTime: 2100, endTime: 2160, confidence: 0.71, severity: "medium"   as Severity, status: "open"      as AlertStatus, title: "Destek koşusu eksikliği",   description: "Top taşıyıcı için pas opsiyonu oluşturulamadı.",                            relatedMetric: "progressive_passes", suggestedClipId: undefined, createdAt: NOW },
  { id: 3006, matchId: 1001, teamId: 1, playerId: 2, alertType: "compactness_lost"       as AlertType, startTime: 2800, endTime: 2870, confidence: 0.68, severity: "high"     as Severity, status: "open"      as AlertStatus, title: "Kompaktlık problemi",        description: "Takım kompaktlığı 28 m'ye çıktı, blok mesafesi aşıldı.",                   relatedMetric: "compactness",    suggestedClipId: undefined, createdAt: NOW },
  // U13 vs Kartal Akademi
  { id: 3007, matchId: 1002, teamId: 2, playerId: 5, alertType: "defensive_line_break"   as AlertType, startTime:  310, endTime:  370, confidence: 0.74, severity: "medium"   as Severity, status: "open"      as AlertStatus, title: "Savunma hattı bozulması",   description: "Sol bek pozisyonu hat dışına çıktı.",                                       relatedMetric: "defensive_line", suggestedClipId: 9004, createdAt: NOW },
  { id: 3008, matchId: 1002, teamId: 2, playerId: 5, alertType: "transition"             as AlertType, startTime:  950, endTime: 1010, confidence: 0.65, severity: "low"      as Severity, status: "resolved"  as AlertStatus, title: "Geçiş organizasyonu",        description: "Top kazanımı sonrası hızlı geçiş fırsatı değerlendirilemedi.",              relatedMetric: "transition_speed", suggestedClipId: undefined, createdAt: NOW },
];

// ── Clips ─────────────────────────────────────────────────────────────────────
export const mockClips = [
  { id: 9001, matchId: 1001, alertId: 3003, playerId: 1, title: "Geçiş savunması açığı",    description: "Top kaybı sonrası 5 sn reaksiyon eksikliği.",  startTime: 1200, endTime: 1260, tag: "transition",      storagePath: "org/1/clips/1001_1200.mp4", thumbnailPath: undefined, createdAt: NOW },
  { id: 9002, matchId: 1001, alertId: 3004, playerId: 3, title: "Derin koşu — sağ kanat",   description: "Savunma arkasına zamanlanmış koşu.",           startTime: 1540, endTime: 1600, tag: "depth_run",       storagePath: "org/1/clips/1001_1540.mp4", thumbnailPath: undefined, createdAt: NOW },
  { id: 9003, matchId: 1001, alertId: 3001, playerId: 2, title: "Savunma hattı kayması",    description: "Hat senkronizasyonu bozulması anı.",           startTime:  450, endTime:  510, tag: "defensive_line",  storagePath: "org/1/clips/1001_450.mp4",  thumbnailPath: undefined, createdAt: NOW },
  { id: 9004, matchId: 1002, alertId: 3007, playerId: 5, title: "Sol bek hat dışı",         description: "Savunma hattı bozulması — sol taraf.",         startTime:  310, endTime:  370, tag: "defensive_line",  storagePath: "org/1/clips/1002_310.mp4",  thumbnailPath: undefined, createdAt: NOW },
];

// ── PlayerMatchPerformances ───────────────────────────────────────────────────
export const mockPerformances = [
  // U15 vs Mavi Spor
  { id: 7201, playerId: 1, matchId: 1001, minutesPlayed: 82, averagePositionX: 0.48, averagePositionY: 0.55, maxSpeed: 31.2, averageSpeed: 22.1, tacticalScore: 7.1, technicalScore: 7.4, physicalScore: 6.8, decisionScore: 7.0, alertsInvolved: 2, positiveActions: 21, developmentNotes: "Orta blok geçişlerinde ilk hamle kalitesi iyileştirilmeli.", createdAt: NOW },
  { id: 7202, playerId: 2, matchId: 1001, minutesPlayed: 90, averagePositionX: 0.22, averagePositionY: 0.50, maxSpeed: 28.4, averageSpeed: 20.3, tacticalScore: 7.6, technicalScore: 6.5, physicalScore: 7.2, decisionScore: 7.0, alertsInvolved: 2, positiveActions: 14, developmentNotes: "Savunma hattı uyumu iyi, derin koşu kapama geliştirilmeli.", createdAt: NOW },
  { id: 7203, playerId: 3, matchId: 1001, minutesPlayed: 78, averagePositionX: 0.72, averagePositionY: 0.44, maxSpeed: 34.8, averageSpeed: 23.5, tacticalScore: 7.0, technicalScore: 7.8, physicalScore: 7.1, decisionScore: 7.3, alertsInvolved: 1, positiveActions: 26, developmentNotes: "Kanat çizgisi ile iç koridor arasındaki seçim daha erken tetiklenmeli.", createdAt: NOW },
  { id: 7204, playerId: 4, matchId: 1001, minutesPlayed: 90, averagePositionX: 0.10, averagePositionY: 0.50, maxSpeed: 22.1, averageSpeed: 14.2, tacticalScore: 7.2, technicalScore: 6.0, physicalScore: 7.0, decisionScore: 7.4, alertsInvolved: 0, positiveActions:  8, developmentNotes: "Uzun pas isabeti yüksek, çıkış kararları gelişiyor.", createdAt: NOW },
  // U13 vs Kartal Akademi
  { id: 7205, playerId: 5, matchId: 1002, minutesPlayed: 75, averagePositionX: 0.18, averagePositionY: 0.52, maxSpeed: 27.6, averageSpeed: 19.8, tacticalScore: 6.8, technicalScore: 6.2, physicalScore: 6.5, decisionScore: 6.4, alertsInvolved: 1, positiveActions: 11, developmentNotes: "Hat disiplini gelişiyor, pozisyon alma hızı artırılmalı.", createdAt: NOW },
  // U17 vs Anadolu FK
  { id: 7206, playerId: 6, matchId: 1003, minutesPlayed: 85, averagePositionX: 0.68, averagePositionY: 0.42, maxSpeed: 33.5, averageSpeed: 22.8, tacticalScore: 6.9, technicalScore: 7.2, physicalScore: 7.5, decisionScore: 7.1, alertsInvolved: 0, positiveActions: 19, developmentNotes: "Bitiricilik ve hareket kalitesi maç boyunca tutarlıydı.", createdAt: NOW },
];


// ── ScoutNotes ────────────────────────────────────────────────────────────────
export const mockScoutingNotes: ScoutNote[] = [
  { id: 8001, playerId: 3, scoutId: 2, note: "Sağ kanatta içeri kesme davranışı çok hızlı. 2. pas kalitesi yüksek.",               rating: 8.4, tagsJson: ["progression", "decision"],        createdAt: NOW },
  { id: 8002, playerId: 1, scoutId: 2, note: "Orta sahada top alma pozisyonlaması iyi. Baskı altında sakin kalabiliyor.",           rating: 7.9, tagsJson: ["composure", "positioning"],       createdAt: NOW },
  { id: 8003, playerId: 4, scoutId: 2, note: "Uzun pas isabeti dikkat çekici. Çıkış kararları maç deneyimiyle gelişiyor.",         rating: 7.5, tagsJson: ["distribution", "decision"],       createdAt: NOW },
  { id: 8004, playerId: 6, scoutId: 2, note: "Ceza sahası içi hareket kalitesi yüksek. Bitiricilik tutarlı.",                      rating: 8.1, tagsJson: ["finishing", "movement"],           createdAt: NOW },
  { id: 8005, playerId: 2, scoutId: 2, note: "Savunma hattı liderliği yapıyor. Derin koşu kapama geliştirilmeli.",                 rating: 7.2, tagsJson: ["leadership", "defensive_line"],   createdAt: NOW },
];

// ── Reports ───────────────────────────────────────────────────────────────────
export const mockReports: Report[] = [
  { id: 7001, matchId: 1001, playerId: undefined, reportType: "match_summary"      satisfies ReportType, title: "U15 Kırmızı Takım vs Mavi Spor — Maç Raporu",  summary: "Baskı tetikleyicileri ve geçiş organizasyonundaki gelişim alanları. 6 taktiksel uyarı tespit edildi.", htmlPath: undefined, pdfPath: "reports/7001.pdf", createdAt: NOW },
  { id: 7002, matchId: undefined, playerId: 4,    reportType: "player_development" satisfies ReportType, title: "Can Öztürk — Oyuncu Gelişim Raporu",            summary: "Uzun pas isabeti ve çıkış kararları ön plana çıkıyor. Gelişim ivmesi: +0.44.",                          htmlPath: undefined, pdfPath: "reports/7002.pdf", createdAt: NOW },
  { id: 7003, matchId: undefined, playerId: undefined, reportType: "scouting"      satisfies ReportType, title: "U15 Scouting Kısa Liste",                       summary: "Kerem Demir ve Arda Yılmaz transfer listesine alındı. Gelişim ivmesi kriterleri karşılandı.",           htmlPath: undefined, pdfPath: "reports/7003.pdf", createdAt: NOW },
  { id: 7004, matchId: undefined, playerId: undefined, reportType: "training"      satisfies ReportType, title: "Mart 2026 Akademi Gelişim Özeti",               summary: "Tüm takımlar için aylık gelişim özeti. Kompaktlık ve geçiş savunması öncelikli çalışma alanları.",    htmlPath: undefined, pdfPath: "reports/7004.pdf", createdAt: NOW },
];

// ── TacticalMetrics ───────────────────────────────────────────────────────────
export const mockMetrics = [
  { id: 6101, matchId: 1001, teamId: 1, timestamp: "2026-04-12T13:12:00.000Z", metricType: "field_tilt"          satisfies MetricType, value: 0.63, unit: "",       metadataJson: { hint: "kanat baskınlığı" }, createdAt: NOW },
  { id: 6102, matchId: 1001, teamId: 1, timestamp: "2026-04-12T13:20:00.000Z", metricType: "ppda"                satisfies MetricType, value: 8.4,  unit: "",       metadataJson: { phase: "pressing" },        createdAt: NOW },
  { id: 6103, matchId: 1001, teamId: 1, timestamp: "2026-04-12T13:30:00.000Z", metricType: "progressive_passes"  satisfies MetricType, value: 11,   unit: "passes", metadataJson: { phase: "transition" },      createdAt: NOW },
  { id: 6104, matchId: 1001, teamId: 1, timestamp: "2026-04-12T13:45:00.000Z", metricType: "xg"                  satisfies MetricType, value: 1.82, unit: "",       metadataJson: {},                           createdAt: NOW },
];


// ── DrillRecommendations ──────────────────────────────────────────────────────
export const mockDrills: DrillRecommendation[] = [
  {
    id: 9101, alertType: "block_gap_wide"          as AlertType, title: "8v8 Kompakt Blok Oyunu",
    problemType: "tactical" as ProblemType, ageCategory: "U15", durationMinutes: 18, playerCount: 16,
    pitchSize: "half" as PitchSize, difficulty: "medium" as DrillDifficulty,
    description: "Savunma ve orta saha bloğu kopukluğunu gidermek için kompakt blok oyunu.",
    coachingPointsJson: [{ tr: "Bloklar arası mesafe 12-15 m aralığında tutulmalı" }, { tr: "Top tarafına birlikte kayma yapılmalı" }, { tr: "Top kaybından sonra ilk reaksiyon 5 saniye içinde gelmeli" }],
    createdAt: NOW,
  },
  {
    id: 9102, alertType: "poor_transition_defense" as AlertType, title: "5 Saniye Karşı Pres Oyunu",
    problemType: "physical" as ProblemType, ageCategory: "U15", durationMinutes: 20, playerCount: 14,
    pitchSize: "half" as PitchSize, difficulty: "hard" as DrillDifficulty,
    description: "Geçiş esnasında hızlı defensive reaksiyon ve press trigger.",
    coachingPointsJson: [{ tr: "Top kaybından sonra ilk 5 saniye pres tetikleme" }, { tr: "Omuz hizası ve doğru açı seçimi" }, { tr: "Yönlendirme ve ikinci dalga koordinasyonu" }],
    createdAt: NOW,
  },
  {
    id: 9103, alertType: "depth_run_opportunity"   as AlertType, title: "Üçüncü Adam Koşusu",
    problemType: "tactical" as ProblemType, ageCategory: "U15", durationMinutes: 16, playerCount: 12,
    pitchSize: "small_sided" as PitchSize, difficulty: "medium" as DrillDifficulty,
    description: "Derin koşu pozisyonlaması ve pas opsiyonu yaratma.",
    coachingPointsJson: [{ tr: "Üçüncü adam pozisyonlaması defans hattının arkasında" }, { tr: "Zamanlanmış çalışma ve pas ritmi" }, { tr: "Defans linesi geçme hareketleri (timing)" }],
    createdAt: NOW,
  },
  {
    id: 9104, alertType: "defensive_line_break"    as AlertType, title: "Savunma Çizgisi Senkronizasyonu",
    problemType: "tactical" as ProblemType, ageCategory: "U15", durationMinutes: 15, playerCount: 8,
    pitchSize: "half" as PitchSize, difficulty: "hard" as DrillDifficulty,
    description: "Savunma çizgisi disiplini ve hat hizasında kalma öğretimi.",
    coachingPointsJson: [{ tr: "Hat uyumu (4 bek aynı hizada kalma)" }, { tr: "Savunma arkası kontrol ve offside hareketleri" }, { tr: "Topla çıkış tekniği (GK ve merkez bek)" }],
    createdAt: NOW,
  },
  {
    id: 9105, alertType: "lack_of_support_run"     as AlertType, title: "Destek Açısı ve Pas Opsiyonu Oyunu",
    problemType: "tactical" as ProblemType, ageCategory: "U15", durationMinutes: 18, playerCount: 14,
    pitchSize: "small_sided" as PitchSize, difficulty: "medium" as DrillDifficulty,
    description: "Top taşıyıcı için her zaman pas opsiyonu yaratma.",
    coachingPointsJson: [{ tr: "Destek koşusu açı seçimi (30-45 derece)" }, { tr: "Orta sahadan gelen derinlik" }, { tr: "Pas ve move kombinasyonları" }],
    createdAt: NOW,
  },
];

// ── Demo constants ────────────────────────────────────────────────────────────

/** Demo login credentials — backend seed ile eşleşir */
export const DEMO_CREDENTIALS = {
  coach: { email: "coach@anadolu-akademi.demo", password: "demo12345" },
  scout: { email: "scout@anadolu-akademi.demo", password: "demo12345" },
} as const;

/**
 * Takım metrikleri — U15 vs Mavi Spor maçından.
 * Tüm sayısal değerler backend seed ile tutarlı.
 */
export const DEMO_TEAM_METRICS = {
  teamLength:                47.2,  // m
  teamWidth:                 42.8,  // m
  compactness:               18.4,  // m
  defenseToMidfieldDistance: 21.4,  // m
  midfieldToAttackDistance:  16.8,  // m
  transitionSpeed:            4.6,  // m/s
  defensiveLineDrift:         5.6,  // m
  alertConfidence:            0.82, // 0-1
  calibrationError:           0.42, // m
  trackingConfidence:         0.87, // 0-1
} as const;

export const demoVideoSrc =
  "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4";
