# Mock Veri Kaldırma Planı - Detaylı Uygulama Rehberi

**Hedef**: Frontend'de hiç mock veri kalmaması  
**Zaman**: 3-4 gün  
**Öncelik**: YÜKSEK

---

## FAZA 1: SCOUTING SAYFASI (1 Gün)

### Mevcut Durum
```typescript
// frontend/app/(app)/scouting/page.tsx
import { mockPlayers, mockScoutingNotes, mockMatches } from "@/data/demo";

const allPlayers = useMemo(() => {
  return mockPlayers
    .filter((p) => p.teamId === teamId)
    .sort((a, b) => (b.developmentVelocity ?? 0) - (a.developmentVelocity ?? 0));
}, [teamId]);
```

### Yapılacaklar

#### 1. API Fonksiyonları Oluştur
```typescript
// frontend/lib/api.ts'ye ekle
export async function apiGetScoutingPlayers(teamId?: number): Promise<ApiResult<Player[]>> {
  if (USE_MOCKS) return ok(mockPlayers as Player[]);
  const r = await req<Player[]>(`/scouting/players${teamId ? `?team_id=${teamId}` : ""}`);
  return r.ok ? r : ok(mockPlayers as Player[]);
}

export async function apiGetScoutingNotes(playerId: number): Promise<ApiResult<ScoutNote[]>> {
  if (USE_MOCKS) return ok(mockScoutingNotes.filter(n => n.playerId === playerId) as ScoutNote[]);
  const r = await req<ScoutNote[]>(`/scouting/players/${playerId}/notes`);
  return r.ok ? r : ok(mockScoutingNotes.filter(n => n.playerId === playerId) as ScoutNote[]);
}
```

#### 2. Backend Endpoints Oluştur
```python
# backend/app/api/scouting.py (YENİ)
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models.player import Player
from app.models.scout_note import ScoutNote

router = APIRouter(prefix="/scouting", tags=["scouting"])

@router.get("/players")
def get_scouting_players(
    team_id: int = None,
    session: Session = Depends(get_session)
):
    """Oyuncu izleme listesi"""
    statement = select(Player)
    if team_id:
        statement = statement.where(Player.team_id == team_id)
    
    players = session.exec(statement).all()
    return sorted(
        players,
        key=lambda p: p.development_velocity or 0,
        reverse=True
    )

@router.get("/players/{player_id}/notes")
def get_player_scout_notes(
    player_id: int,
    session: Session = Depends(get_session)
):
    """Oyuncu izleme notları"""
    statement = select(ScoutNote).where(ScoutNote.player_id == player_id)
    return session.exec(statement).all()
```

#### 3. Frontend Sayfasını Güncelle
```typescript
// frontend/app/(app)/scouting/page.tsx
"use client";

import { useEffect, useState, useMemo } from "react";
import { apiGetScoutingPlayers, apiGetScoutingNotes } from "@/lib/api";
import type { Player, ScoutNote } from "@/types/domain";

export default function ScoutingPage() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [notes, setNotes] = useState<Record<number, ScoutNote[]>>({});
  const [loading, setLoading] = useState(true);
  const [teamId, setTeamId] = useState<number | null>(null);

  useEffect(() => {
    const fetchPlayers = async () => {
      setLoading(true);
      const result = await apiGetScoutingPlayers(teamId || undefined);
      if (result.ok) {
        setPlayers(result.data);
        
        // Fetch notes for each player
        for (const player of result.data) {
          const notesResult = await apiGetScoutingNotes(player.id);
          if (notesResult.ok) {
            setNotes(prev => ({
              ...prev,
              [player.id]: notesResult.data
            }));
          }
        }
      }
      setLoading(false);
    };

    fetchPlayers();
  }, [teamId]);

  if (loading) return <div>Yükleniyor...</div>;

  return (
    <div className="space-y-6">
      {/* Sayfa içeriği */}
      {players.map(player => (
        <div key={player.id}>
          <h3>{player.firstName} {player.lastName}</h3>
          <p>Gelişim Hızı: {player.developmentVelocity}</p>
          {notes[player.id]?.map(note => (
            <div key={note.id}>{note.note}</div>
          ))}
        </div>
      ))}
    </div>
  );
}
```

---

## FAZA 2: DRILLS SAYFASI (1 Gün)

### Mevcut Durum
```typescript
// frontend/app/(app)/drills/page.tsx
import { mockDrills } from "@/data/demo";

const filteredDrills = useMemo(() => {
  return mockDrills.filter((d) => {
    if (searchQ && !`${d.title} ${d.problemType}`.toLowerCase().includes(searchQ.toLowerCase())) return false;
    if (selectedProblems.length && !selectedProblems.some((p) => PROBLEM_MAP[p].alerts.includes(d.alertType))) return false;
    return true;
  });
}, [searchQ, selectedProblems]);
```

### Yapılacaklar

#### 1. API Fonksiyonları Oluştur
```typescript
// frontend/lib/api.ts'ye ekle
export async function apiGetDrills(
  alertType?: string,
  problemType?: string
): Promise<ApiResult<DrillRecommendation[]>> {
  if (USE_MOCKS) return ok(mockDrills as DrillRecommendation[]);
  
  const params = new URLSearchParams();
  if (alertType) params.append("alert_type", alertType);
  if (problemType) params.append("problem_type", problemType);
  
  const r = await req<DrillRecommendation[]>(`/drills?${params.toString()}`);
  return r.ok ? r : ok(mockDrills as DrillRecommendation[]);
}
```

#### 2. Backend Endpoints Oluştur
```python
# backend/app/api/drills.py (YENİ)
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from app.database import get_session
from app.models.drill_recommendation import DrillRecommendation

router = APIRouter(prefix="/drills", tags=["drills"])

@router.get("")
def get_drills(
    alert_type: str = Query(None),
    problem_type: str = Query(None),
    session: Session = Depends(get_session)
):
    """Antrenman önerileri"""
    statement = select(DrillRecommendation)
    
    if alert_type:
        statement = statement.where(DrillRecommendation.alert_type == alert_type)
    if problem_type:
        statement = statement.where(DrillRecommendation.problem_type == problem_type)
    
    return session.exec(statement).all()
```

#### 3. Frontend Sayfasını Güncelle
```typescript
// frontend/app/(app)/drills/page.tsx
"use client";

import { useEffect, useState, useMemo } from "react";
import { apiGetDrills } from "@/lib/api";
import type { DrillRecommendation } from "@/types/domain";

export default function DrillsPage() {
  const [drills, setDrills] = useState<DrillRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQ, setSearchQ] = useState("");
  const [selectedProblems, setSelectedProblems] = useState<string[]>([]);

  useEffect(() => {
    const fetchDrills = async () => {
      setLoading(true);
      const result = await apiGetDrills();
      if (result.ok) {
        setDrills(result.data);
      }
      setLoading(false);
    };

    fetchDrills();
  }, []);

  const filteredDrills = useMemo(() => {
    return drills.filter((d) => {
      if (searchQ && !`${d.title} ${d.problemType}`.toLowerCase().includes(searchQ.toLowerCase())) return false;
      if (selectedProblems.length && !selectedProblems.some((p) => PROBLEM_MAP[p].alerts.includes(d.alertType))) return false;
      return true;
    });
  }, [drills, searchQ, selectedProblems]);

  if (loading) return <div>Yükleniyor...</div>;

  return (
    <div className="space-y-6">
      {/* Sayfa içeriği */}
      {filteredDrills.map(drill => (
        <div key={drill.id}>{drill.title}</div>
      ))}
    </div>
  );
}
```

---

## FAZA 3: DIĞER SAYFALAR (1 Gün)

### `/teams/[id]` Sayfası
```typescript
// BEFORE
const team = useMemo(() => mockTeams.find((t) => t.id === teamId), [teamId]);
const players = useMemo(() => mockPlayers.filter((p) => p.teamId === teamId), [teamId]);

// AFTER
const [team, setTeam] = useState<Team | null>(null);
const [players, setPlayers] = useState<Player[]>([]);

useEffect(() => {
  const fetchTeam = async () => {
    const result = await apiGetTeamById(teamId);
    if (result.ok) setTeam(result.data);
  };
  
  const fetchPlayers = async () => {
    const result = await apiGetPlayers(teamId);
    if (result.ok) setPlayers(result.data);
  };
  
  fetchTeam();
  fetchPlayers();
}, [teamId]);
```

### `/players/[id]` Sayfası
```typescript
// BEFORE
const player = useMemo(() => mockPlayers.find(p => p.id === playerId), [playerId]);
const performances = useMemo(() => mockPerformances.filter(x => x.playerId === playerId), [playerId]);
const clips = useMemo(() => mockClips.filter(c => c.playerId === playerId), [playerId]);

// AFTER
const [player, setPlayer] = useState<Player | null>(null);
const [performances, setPerformances] = useState<PlayerPerformance[]>([]);
const [clips, setClips] = useState<Clip[]>([]);

useEffect(() => {
  const fetchData = async () => {
    const playerResult = await apiGetPlayerById(playerId);
    if (playerResult.ok) setPlayer(playerResult.data);
    
    const perfResult = await apiGetPlayerPerformances(playerId);
    if (perfResult.ok) setPerformances(perfResult.data);
    
    const clipsResult = await apiGetPlayerClips(playerId);
    if (clipsResult.ok) setClips(clipsResult.data);
  };
  
  fetchData();
}, [playerId]);
```

### `/settings` Sayfası
```typescript
// BEFORE
const [roster, setRoster] = useState<Player[]>(() => mockPlayers.slice(0, 12));

// AFTER
const [roster, setRoster] = useState<Player[]>([]);

useEffect(() => {
  const fetchRoster = async () => {
    const result = await apiGetPlayers();
    if (result.ok) setRoster(result.data.slice(0, 12));
  };
  
  fetchRoster();
}, []);
```

---

## FAZA 4: FALLBACK MEKANIZMASI (1 Gün)

### Tutarlı Fallback Hook Oluştur
```typescript
// frontend/hooks/useDataWithFallback.ts (YENİ)
import { useEffect, useState } from "react";
import type { ApiResult } from "@/lib/api";

export function useDataWithFallback<T>(
  apiCall: () => Promise<ApiResult<T>>,
  fallbackData: T,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T>(fallbackData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await apiCall();
        
        if (result.ok) {
          setData(result.data);
          setError(null);
        } else {
          setData(fallbackData);
          setError(result.error?.message || "Veri yüklenemedi");
        }
      } catch (err) {
        setData(fallbackData);
        setError(err instanceof Error ? err.message : "Hata oluştu");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, dependencies);

  return { data, loading, error };
}
```

### Kullanım Örneği
```typescript
// Sayfada
const { data: players, loading } = useDataWithFallback(
  () => apiGetScoutingPlayers(teamId),
  [],
  [teamId]
);
```

---

## FAZA 5: MOCK VERİ DOSYASINI TEMIZLE (1 Gün)

### Adım 1: Tüm Import'ları Kontrol Et
```bash
# Tüm mock import'larını bul
grep -r "from.*demo" frontend/app --include="*.tsx" --include="*.ts"

# Sonuç:
# frontend/app/(app)/components/page.tsx (Silinebilir - demo sayfası)
# frontend/app/(app)/scouting/page.tsx (Kaldırıldı)
# frontend/app/(app)/drills/page.tsx (Kaldırıldı)
# ... vb
```

### Adım 2: Demo Sayfasını Gizle
```typescript
// frontend/app/(app)/components/page.tsx
// Başına ekle:
// @deprecated - Bu sayfa sadece bileşen galerisi için. Production'da gizlenecek.

// Veya tamamen sil
```

### Adım 3: Mock Veri Dosyasını Kaldır
```bash
# Adım 1: Backup al
cp frontend/data/demo.ts frontend/data/demo.ts.backup

# Adım 2: Tüm import'ları kontrol et
grep -r "demo" frontend --include="*.tsx" --include="*.ts" | grep -v ".backup"

# Adım 3: Hiç import kalmadığını doğrula
# Adım 4: Dosyayı sil
rm frontend/data/demo.ts
```

---

## FAZA 6: TEST VE DOĞRULAMA (1 Gün)

### Test Checklist
```bash
# 1. Tüm sayfaları test et
- [ ] /scouting - Gerçek oyuncu verileri gösteriyor
- [ ] /drills - Gerçek antrenman önerileri gösteriyor
- [ ] /teams/[id] - Gerçek takım verileri gösteriyor
- [ ] /players/[id] - Gerçek oyuncu verileri gösteriyor
- [ ] /settings - Gerçek ayarlar gösteriyor
- [ ] /matches - Gerçek maç verileri gösteriyor
- [ ] /matches/[id] - Gerçek maç detayları gösteriyor

# 2. Fallback mekanizmasını test et
- [ ] Backend kapalı iken fallback çalışıyor
- [ ] Hata mesajları gösteriliyor
- [ ] Sayfa çökmüyor

# 3. TypeScript kontrol
- [ ] npx tsc --noEmit (Hata yok)

# 4. Build kontrol
- [ ] npm run build (Başarılı)

# 5. Runtime kontrol
- [ ] npm run dev (Hata yok)
- [ ] Browser console temiz (Uyarı yok)
```

### Doğrulama Komutları
```bash
# Mock import'ları ara
grep -r "mockMatches\|mockPlayers\|mockAlerts\|mockClips\|mockDrills\|mockReports\|mockVideos\|mockMetrics\|mockPerformances\|mockScoutingNotes" frontend/app --include="*.tsx" --include="*.ts"

# Sonuç boş olmalı (sadece test dosyaları hariç)
```

---

## FAZA 7: BACKEND ENDPOINTS OLUŞTUR

### Gerekli Endpoints
```python
# backend/app/api/scouting.py
GET /api/scouting/players
GET /api/scouting/players/{player_id}/notes
POST /api/scouting/players/{player_id}/notes

# backend/app/api/drills.py
GET /api/drills
GET /api/drills/{drill_id}

# backend/app/api/teams.py (Mevcut, güncelle)
GET /api/teams/{team_id}
GET /api/teams/{team_id}/players

# backend/app/api/players.py (Mevcut, güncelle)
GET /api/players/{player_id}
GET /api/players/{player_id}/performances
GET /api/players/{player_id}/clips
```

### Backend Modelleri
```python
# backend/app/models/scout_note.py (Kontrol et)
class ScoutNote(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player.id")
    scout_id: int = Field(foreign_key="user.id")
    note: str
    rating: float | None = None
    tags_json: dict | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# backend/app/models/drill_recommendation.py (Kontrol et)
class DrillRecommendation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    alert_type: str
    title: str
    description: str
    problem_type: str
    difficulty: str
    duration_minutes: int
    # ... vb
```

---

## ZAMAN ÇIZELGESI

| Gün | Görev | Durum |
|-----|-------|-------|
| 1 | Scouting sayfası | ⏳ Yapılacak |
| 2 | Drills sayfası | ⏳ Yapılacak |
| 3 | Diğer sayfalar | ⏳ Yapılacak |
| 4 | Fallback mekanizması | ⏳ Yapılacak |
| 5 | Mock veri dosyasını temizle | ⏳ Yapılacak |
| 6 | Test ve doğrulama | ⏳ Yapılacak |
| 7 | Backend endpoints | ⏳ Yapılacak |

---

## BAŞARI KRİTERLERİ

✅ **Tamamlandı Sayılacak**:
- [ ] Frontend'de hiç mock import yok
- [ ] Tüm sayfalar gerçek API'den veri alıyor
- [ ] Fallback mekanizması çalışıyor
- [ ] TypeScript hata yok
- [ ] Build başarılı
- [ ] Tüm sayfalar test edildi
- [ ] Browser console temiz

---

## NOTLAR

- **Backup Al**: Değişiklik yapmadan önce git commit yap
- **Kademeli Rollout**: Bir sayfayı tamamen bitir, sonra diğerine geç
- **Test Sık**: Her değişiklikten sonra test et
- **Dokümantasyon**: Değişiklikleri dokümante et

