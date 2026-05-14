"""
Gizlilik ve uyumluluk modelleri — U8-U17 oyuncu veri güvenliği.

TODO: Bu modeller şu an placeholder'dır. Gerçek implementasyon için:
  - Hukuki danışmanlık alınmalı (KVKK madde 6 — özel nitelikli kişisel veri)
  - Veli onayı formları avukat tarafından hazırlanmalı
  - Veri işleme envanteri oluşturulmalı
  - Alembic migration yazılmalı
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from sqlalchemy import Column, DateTime, Enum as SAEnum, JSON
from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin


# ── Enums ─────────────────────────────────────────────────────────────────────

class ConsentType(str, Enum):
    """Onay türleri."""
    VIDEO_RECORDING   = "video_recording"    # Video kaydı
    DATA_PROCESSING   = "data_processing"    # Kişisel veri işleme
    PERFORMANCE_ANALYSIS = "performance_analysis"  # Performans analizi
    PHOTO_SHARING     = "photo_sharing"      # Fotoğraf paylaşımı
    THIRD_PARTY_SHARE = "third_party_share"  # Üçüncü taraf paylaşımı


class ConsentStatus(str, Enum):
    GRANTED   = "granted"    # Onay verildi
    REVOKED   = "revoked"    # Onay geri alındı
    PENDING   = "pending"    # Onay bekleniyor
    EXPIRED   = "expired"    # Onay süresi doldu


class AuditAction(str, Enum):
    """Denetim kaydı eylem türleri."""
    DATA_EXPORT      = "data_export"       # Veri dışa aktarımı
    DATA_ANONYMIZE   = "data_anonymize"    # Veri anonimleştirme
    DATA_DELETE      = "data_delete"       # Veri silme talebi
    CONSENT_GRANT    = "consent_grant"     # Onay verildi
    CONSENT_REVOKE   = "consent_revoke"    # Onay geri alındı
    PLAYER_VIEW      = "player_view"       # Oyuncu verisi görüntülendi
    REPORT_GENERATE  = "report_generate"   # Rapor oluşturuldu
    VIDEO_PROCESS    = "video_process"     # Video işlendi


# ── Models ────────────────────────────────────────────────────────────────────

class ParentalConsent(TimestampMixin, SQLModel, table=True):
    """
    Veli onayı kaydı — U8-U17 oyuncular için zorunlu.

    TODO:
    - Onay formunun PDF kopyası storage'a yüklenmeli
    - Onay süresi (expiry_date) takip edilmeli
    - Sezon başında yenileme hatırlatması gönderilmeli
    - KVKK kapsamında saklama süresi belirlenmeli
    """
    __tablename__ = "parental_consent"

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player.id", index=True)
    organization_id: int = Field(foreign_key="organization.id", index=True)

    # Veli bilgileri
    guardian_full_name: str = Field(max_length=256)
    guardian_email: Optional[str] = Field(default=None, max_length=256)
    guardian_phone: Optional[str] = Field(default=None, max_length=64)
    relationship: str = Field(default="parent", max_length=64)  # parent, guardian, other

    # Onay detayları
    consent_type: ConsentType = Field(
        sa_column=Column(
            SAEnum(ConsentType, values_callable=lambda o: [e.value for e in o],
                   native_enum=False, length=48),
            nullable=False,
        )
    )
    status: ConsentStatus = Field(
        sa_column=Column(
            SAEnum(ConsentStatus, values_callable=lambda o: [e.value for e in o],
                   native_enum=False, length=32),
            nullable=False,
        )
    )

    consent_date: Optional[date] = Field(default=None)
    expiry_date: Optional[date] = Field(default=None)

    # Onay belgesi (PDF path veya URL)
    document_path: Optional[str] = Field(default=None, max_length=1024)

    # Ek notlar
    notes: Optional[str] = Field(default=None)


class AuditLog(TimestampMixin, SQLModel, table=True):
    """
    Denetim kaydı — veri erişim ve işlem geçmişi.

    TODO:
    - Tüm kişisel veri erişimleri buraya kaydedilmeli
    - Saklama süresi politikası belirlenmeli (ör. 2 yıl)
    - Düzenli dışa aktarım ve arşivleme planlanmalı
    - Yetkisiz erişim tespiti için alert mekanizması eklenmeli
    """
    __tablename__ = "audit_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: Optional[int] = Field(default=None, foreign_key="organization.id", index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    player_id: Optional[int] = Field(default=None, foreign_key="player.id", index=True)

    action: AuditAction = Field(
        sa_column=Column(
            SAEnum(AuditAction, values_callable=lambda o: [e.value for e in o],
                   native_enum=False, length=48),
            nullable=False,
        )
    )

    # İşlem detayları (JSON)
    details: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )

    # İstek kaynağı
    ip_address: Optional[str] = Field(default=None, max_length=64)
    user_agent: Optional[str] = Field(default=None, max_length=512)

    # Başarı durumu
    success: bool = Field(default=True)
    error_message: Optional[str] = Field(default=None)
