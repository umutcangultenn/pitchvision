from typing import Optional
from pydantic import BaseModel, Field


class AppSettingsRead(BaseModel):
    app_name: str
    debug: bool
    api_version: str = "v1"
    default_language: str = "tr"


class AppSettingsUpdate(BaseModel):
    default_language: str = Field(default="tr", max_length=8)


# Organization Settings
class OrganizationSettingsRead(BaseModel):
    id: int
    name: str
    city: str
    logo_url: Optional[str] = None
    organization_type: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None


class OrganizationSettingsUpdate(BaseModel):
    name: str = Field(max_length=255)
    city: str = Field(max_length=128)
    logo_url: Optional[str] = None
    organization_type: str = Field(max_length=64)
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None


# User Management
class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: Optional[str] = None


class UserInviteRequest(BaseModel):
    email: str
    full_name: str
    role: str


# Team Settings
class TeamRead(BaseModel):
    id: int
    name: str
    age_category: str
    game_format: str
    default_formation: str
    pitch_length: float
    pitch_width: float
    season: str
    is_active: bool


class TeamCreateRequest(BaseModel):
    name: str = Field(max_length=255)
    age_category: str = Field(max_length=32)
    game_format: str = Field(max_length=32)
    default_formation: str = Field(max_length=32)
    pitch_length: float
    pitch_width: float
    season: Optional[str] = Field(default=None, max_length=32)
    organization_id: Optional[int] = Field(default=None)


# Season Settings
class SeasonRead(BaseModel):
    id: int
    name: str
    start_date: str
    end_date: str
    is_active: bool
    teams_count: int


# Video Processing Settings
class VideoProcessingSettingsRead(BaseModel):
    default_pitch_size: str
    default_game_format: str
    detection_confidence_threshold: float
    alert_threshold_value: float
    default_clip_duration: int  # seconds


class VideoProcessingSettingsUpdate(BaseModel):
    default_pitch_size: str
    default_game_format: str
    detection_confidence_threshold: float = Field(ge=0.0, le=1.0)
    alert_threshold_value: float = Field(ge=0.0, le=1.0)
    default_clip_duration: int = Field(ge=5, le=120)


# Notification Settings
class NotificationSettingsRead(BaseModel):
    notify_analysis_complete: bool
    notify_errors: bool
    notify_new_report: bool
    notify_scout_note: bool
    notify_player_development: bool


class NotificationSettingsUpdate(BaseModel):
    notify_analysis_complete: bool = True
    notify_errors: bool = True
    notify_new_report: bool = True
    notify_scout_note: bool = True
    notify_player_development: bool = True


# Privacy Settings
class PrivacySettingsRead(BaseModel):
    anonymize_player_data: bool
    gdpr_enabled: bool
    parental_consent_required: bool
    u8_u17_data_security_enabled: bool


class PrivacySettingsUpdate(BaseModel):
    anonymize_player_data: bool = False
    gdpr_enabled: bool = True
    parental_consent_required: bool = True
    u8_u17_data_security_enabled: bool = True


class SubscriptionRead(BaseModel):
    plan_name: str
    billing_cycle: str
    next_renewal: str
    seats_used: int
    seats_limit: int
    status: str


class DroneChecklistRead(BaseModel):
    flight_permission_checked: bool
    pitch_safety_secured: bool
    parent_player_consents_checked: bool
    camera_angle_ok: bool
    pitch_lines_visible: bool
    wind_weather_ok: bool


class DroneChecklistUpdate(BaseModel):
    flight_permission_checked: bool = False
    pitch_safety_secured: bool = False
    parent_player_consents_checked: bool = False
    camera_angle_ok: bool = False
    pitch_lines_visible: bool = False
    wind_weather_ok: bool = False

