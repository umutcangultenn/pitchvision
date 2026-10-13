export type PlanId = "starter" | "academy" | "club" | "pro_analysis";

export type SaaSPlan = {
  id: PlanId;
  name: string;
  tagline: string;
  /** Aylık maç analizi kotası */
  monthlyMatchAnalysis: string;
  /** Kadro / pasaport için üst sınır */
  playerSlots: string;
  videoStorage: string;
  reportExport: string;
  scoutingModule: string;
  premiumSupport: string;
  pricePlaceholder: string;
  /** Vurgulu plan (ör. önerilen) */
  recommended?: boolean;
};

export const PRICING_PLANS: SaaSPlan[] = [
  {
    id: "starter",
    name: "Starter",
    tagline: "Tek takım, temel analiz ile başlamak için ideal.",
    monthlyMatchAnalysis: "8 maç / ay",
    playerSlots: "80 oyuncuya kadar",
    videoStorage: "25 GB depolama",
    reportExport: "PDF rapor (temel)",
    scoutingModule: "Scouting modülü yok",
    premiumSupport: "Standart yardım merkezi",
    pricePlaceholder: "₺— / ay (örnek)",
  },
  {
    id: "academy",
    name: "Academy",
    tagline: "Akademiler için dengeli güç ve görünürlük.",
    monthlyMatchAnalysis: "20 maç / ay",
    playerSlots: "250 oyuncuya kadar",
    videoStorage: "100 GB depolama",
    reportExport: "PDF + CSV dışa aktarım",
    scoutingModule: "Scouting modülü dahil",
    premiumSupport: "E-posta ile öncelikli destek",
    pricePlaceholder: "₺— / ay (örnek)",
    recommended: true,
  },
  {
    id: "club",
    name: "Club",
    tagline: "Birden fazla yaş grubu ve yoğun maç trafiği için.",
    monthlyMatchAnalysis: "45 maç / ay",
    playerSlots: "600 oyuncuya kadar",
    videoStorage: "500 GB depolama",
    reportExport: "Tüm rapor formatları",
    scoutingModule: "Scouting + kısa listeler",
    premiumSupport: "Premium destek (mesai içi hızlı dönüş)",
    pricePlaceholder: "₺— / ay (örnek)",
  },
  {
    id: "pro_analysis",
    name: "Pro Analysis",
    tagline: "Performans merkezleri ve profesyonel analiz ekipleri.",
    monthlyMatchAnalysis: "100 maç / ay",
    playerSlots: "2.000 oyuncuya kadar",
    videoStorage: "2 TB depolama",
    reportExport: "Özelleştirilebilir şablonlar + API (yol haritası)",
    scoutingModule: "Gelişmiş scouting ve karşılaştırma",
    premiumSupport: "7/24 öncelikli hat (kurumsal)",
    pricePlaceholder: "Teklif üzerine (örnek)",
  },
];

/** Ayarlar / faturalama ekranında gösterilen örnek kullanım (demo). */
export const DEMO_SAAS_USAGE = {
  matchesUsed: 8,
  matchesCap: 20,
  storageUsedGb: 72,
  storageCapGb: 100,
  passportUsed: 146,
  passportCap: 250,
  reportExportsUsed: 32,
  reportExportsCap: 60,
};

export const DEMO_INTEREST_MODULES = [
  { value: "match_analysis", label: "Maç analizi & taktik uyarılar" },
  { value: "player_passport", label: "Oyuncu pasaportu & gelişim" },
  { value: "scouting", label: "Scouting modülü" },
  { value: "drills", label: "Antrenman önerileri" },
  { value: "video", label: "Video işleme & kalibrasyon" },
  { value: "full_platform", label: "Tüm platform (genel)" },
] as const;

export const DEMO_REQUEST_ROLES = [
  { value: "club_director", label: "Kulüp yöneticisi" },
  { value: "head_coach", label: "Baş antrenör" },
  { value: "coach", label: "Antrenör" },
  { value: "analyst", label: "Analist" },
  { value: "academy_coordinator", label: "Akademi koordinatörü" },
  { value: "other", label: "Diğer" },
] as const;
