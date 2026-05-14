export type OrganizationType = "academy" | "club" | "school";

export type UserRole = "admin" | "coach" | "scout" | "analyst" | "viewer";

export type MatchStatus = "scheduled" | "live" | "processing" | "completed" | "cancelled";

export type VideoSource = "file_upload" | "url_stream" | "youtube" | "other";

export type VideoAssetStatus = "uploading" | "processing" | "ready" | "failed";

export type AlertType =
  | "pressing"
  | "counter_attack"
  | "transition"
  | "set_piece"
  | "wing_overload"
  | "half_space"
  | "duel"
  | "line_breaking_pass"
  // tactical analytics engine types
  | "defensive_line_break"
  | "block_gap_wide"
  | "depth_run_opportunity"
  | "poor_transition_defense"
  | "compactness_lost"
  | "lack_of_support_run"
  | "other";

export type Severity = "low" | "medium" | "high" | "critical";

export type AlertStatus = "open" | "in_review" | "resolved" | "dismissed";

export type ReportType = "match_summary" | "player_development" | "scouting" | "tactical" | "training";

export type MetricType = "pass_network" | "ppda" | "progressive_passes" | "xg" | "field_tilt" | "custom";

export type ProblemType = "technical" | "tactical" | "physical" | "decision";

export type PitchSize = "full" | "half" | "small_sided";

export type DrillDifficulty = "easy" | "medium" | "hard";

export type Organization = {
  id: number;
  name: string;
  city: string;
  logoUrl?: string;
  organizationType: OrganizationType;
  createdAt: string;
};

export type Team = {
  id: number;
  organizationId: number;
  name: string;
  ageCategory: string;
  gameFormat: string;
  defaultFormation: string;
  pitchLength: number;
  pitchWidth: number;
  season: string;
  createdAt: string;
};

export type Player = {
  id: number;
  organizationId: number;
  teamId?: number;
  firstName: string;
  lastName: string;
  birthDate: string;
  position: string;
  dominantFoot: string;
  heightCm?: number;
  weightKg?: number;
  photoUrl?: string;
  technicalScore?: number;
  tacticalScore?: number;
  physicalScore?: number;
  decisionScore?: number;
  developmentVelocity?: number;
  createdAt: string;
};

export type Match = {
  id: number;
  organizationId: number;
  teamId: number;
  opponentName: string;
  matchDate: string;
  ageCategory: string;
  gameFormat: string;
  pitchLength: number;
  pitchWidth: number;
  firstHalfAttackDirection: string;
  scoreFor: number;
  scoreAgainst: number;
  videoSource: VideoSource;
  status: MatchStatus;
  createdAt: string;
};

export type VideoAsset = {
  id: number;
  matchId: number;
  fileName: string;
  storagePath: string;
  durationSeconds?: number;
  width?: number;
  height?: number;
  fps?: number;
  status: VideoAssetStatus;
  createdAt: string;
};

export type FieldCalibration = {
  id: number;
  matchId: number;
  frameTime: number;
  pointsJson: Record<string, unknown>;
  homographyJson: Record<string, unknown>;
  averageErrorM?: number;
  quality?: number;
  createdAt: string;
};

export type TrackPoint = {
  id: number;
  matchId: number;
  playerId?: number;
  trackId: string;
  teamId?: number;
  frameIndex: number;
  timestamp: string;
  className: string;
  bboxJson: Record<string, unknown>;
  pixelX?: number;
  pixelY?: number;
  fieldX?: number;
  fieldY?: number;
  confidence?: number;
};

export type TacticalMetric = {
  id: number;
  matchId: number;
  teamId: number;
  timestamp: string;
  metricType: MetricType;
  value: number;
  unit: string;
  metadataJson?: Record<string, unknown>;
  createdAt: string;
};

export type TacticalAlert = {
  id: number;
  matchId: number;
  teamId: number;
  playerId?: number;
  trackId?: string;
  alertType: AlertType;
  startTime: number;
  endTime: number;
  confidence?: number;
  severity: Severity;
  status: AlertStatus;
  title: string;
  description?: string;
  relatedMetric?: string;
  suggestedClipId?: number;
  createdAt: string;
};

export type Clip = {
  id: number;
  matchId: number;
  alertId?: number;
  playerId?: number;
  title: string;
  description?: string;
  startTime: number;
  endTime: number;
  tag?: string;
  storagePath: string;
  thumbnailPath?: string;
  createdAt: string;
};

export type PlayerMatchPerformance = {
  id: number;
  playerId: number;
  matchId: number;
  minutesPlayed?: number;
  averagePositionX?: number;
  averagePositionY?: number;
  maxSpeed?: number;
  averageSpeed?: number;
  tacticalScore?: number;
  technicalScore?: number;
  physicalScore?: number;
  decisionScore?: number;
  alertsInvolved?: number;
  positiveActions?: number;
  developmentNotes?: string;
  createdAt: string;
};

export type ScoutNote = {
  id: number;
  playerId: number;
  scoutId: number;
  note: string;
  rating?: number;
  tagsJson?: string[];
  createdAt: string;
};

export type Report = {
  id: number;
  matchId?: number;
  playerId?: number;
  reportType: ReportType;
  title: string;
  summary?: string;
  htmlPath?: string;
  pdfPath?: string;
  createdAt: string;
};

export type DrillRecommendation = {
  id: number;
  alertType: AlertType;
  title: string;
  problemType: ProblemType;
  ageCategory: string;
  durationMinutes: number;
  playerCount: number;
  pitchSize: PitchSize;
  difficulty: DrillDifficulty;
  description?: string;
  coachingPointsJson?: { tr?: string; [k: string]: unknown }[];
  createdAt: string;
};

export type AppAuthUser = {
  id: number;
  email: string;
  fullName: string;
  role: UserRole;
  organizationId: number;
  isActive: boolean;
};

export type CalibrationPoint = {
  id: string;
  label: string;
  description: string;
  x?: number; // pixel coordinates
  y?: number; // pixel coordinates
  fieldX?: number; // real field coordinates in meters
  fieldY?: number; // real field coordinates in meters
  isRequired: boolean;
  isMarked: boolean;
};

export type CalibrationResult = {
  averageError: number;
  quality: "poor" | "fair" | "good" | "excellent";
  pointCount: number;
  homographyMatrix?: number[][];
};

export type VideoEvent = {
  id: string;
  type: "alert" | "clip" | "goal" | "card" | "substitution";
  timestamp: number; // seconds
  title: string;
  description?: string;
  severity?: Severity;
  confidence?: number;
};

export type OverlayType = 
  | "players" 
  | "player_ids" 
  | "formation" 
  | "defense_line" 
  | "block_distance" 
  | "ball_trajectory" 
  | "heatmap" 
  | "tactical_alerts" 
  | "pitch_zones";

export type TeamMetrics = {
  teamLength: number; // meters
  teamWidth: number; // meters  
  compactness: number; // meters
  defenseToMidfieldDistance: number; // meters
  midfieldToAttackDistance: number; // meters
  transitionSpeed: number; // m/s
};

