"""Demo data for report endpoint."""

DEMO_REPORT_DATA = dict(
    match_data={
        "teamName": "U15 Kırmızı Takım",
        "opponentName": "Beyazgöl Spor",
        "matchDate": "2026-04-12T13:00:00.000Z",
        "ageCategory": "U15",
        "scoreFor": 3,
        "scoreAgainst": 2,
        "videoSource": "file_upload",
        "calibrationQuality": "good",
        "trackingConfidence": 0.94,
    },
    alerts_data=[
        {
            "id": 3001, "alertType": "transition", "startTime": 1200,
            "confidence": 0.82, "severity": "high",
            "title": "Hızlı geçiş fırsatı",
            "description": "Orta blokta top kazanımı sonrası kanat boşluğu.",
            "suggestedClipId": 9001,
        },
        {
            "id": 3002, "alertType": "defensive_line_break", "startTime": 430,
            "confidence": 0.78, "severity": "critical",
            "title": "Savunma hattı bozulması",
            "description": "Sol kanat oyuncusu hattan 6m geride kaldı.",
            "suggestedClipId": 9002,
        },
        {
            "id": 3003, "alertType": "block_gap_wide", "startTime": 1810,
            "confidence": 0.66, "severity": "high",
            "title": "Bloklar arası kopukluk",
            "description": "Savunma-orta saha mesafesi 28m'ye ulaştı.",
            "suggestedClipId": 9003,
        },
        {
            "id": 3004, "alertType": "depth_run_opportunity", "startTime": 720,
            "confidence": 0.71, "severity": "medium",
            "title": "Derin koşu fırsatı",
            "description": "Rakip savunma hattı yüksek, arkası açık.",
            "suggestedClipId": None,
        },
    ],
    clips_data=[
        {"id": 9001, "title": "Kanattan yarım alan kırılımı", "description": "Top kazanımı sonrası 2. pasla içeri giriş.", "startTime": 1234, "endTime": 1289, "tag": "transition", "alertId": 3001, "playerId": 2},
        {"id": 9002, "title": "Savunma hattı bozulması", "description": "Sol kanat geride kaldı.", "startTime": 430, "endTime": 510, "tag": "defensive_line", "alertId": 3002, "playerId": 3},
        {"id": 9003, "title": "Blok mesafe açılması", "description": "Orta saha geri çekildi.", "startTime": 1810, "endTime": 1870, "tag": "block_gap", "alertId": 3003, "playerId": 1},
    ],
    players_data=[
        {"id": 1, "firstName": "Ayşe", "lastName": "Demir", "position": "CM", "tacticalScore": 7.0, "technicalScore": 7.2, "physicalScore": 6.5, "decisionScore": 6.9},
        {"id": 2, "firstName": "Kaan", "lastName": "Yılmaz", "position": "LW", "tacticalScore": 7.1, "technicalScore": 7.8, "physicalScore": 7.0, "decisionScore": 7.3},
        {"id": 3, "firstName": "Efe", "lastName": "Çelik", "position": "CB", "tacticalScore": 7.6, "technicalScore": 6.4, "physicalScore": 7.2, "decisionScore": 7.0},
    ],
    performances_data=[
        {"playerId": 1, "minutesPlayed": 68, "tacticalScore": 7.0, "technicalScore": 7.2, "physicalScore": 6.5, "decisionScore": 6.9, "alertsInvolved": 1, "maxSpeed": 32.4, "developmentNotes": "Orta blok geçişlerinde ilk hamle kalitesi iyileştirilmeli."},
        {"playerId": 2, "minutesPlayed": 74, "tacticalScore": 7.1, "technicalScore": 7.8, "physicalScore": 7.0, "decisionScore": 7.3, "alertsInvolved": 1, "maxSpeed": 35.1, "developmentNotes": "Kanat çizgisi ile iç koridor arasındaki seçim daha erken tetiklenmeli."},
        {"playerId": 3, "minutesPlayed": 80, "tacticalScore": 7.6, "technicalScore": 6.4, "physicalScore": 7.2, "decisionScore": 7.0, "alertsInvolved": 1, "maxSpeed": 30.2, "developmentNotes": "Savunma hattı senkronizasyonu geliştirilmeli."},
    ],
    team_shape_data={
        "teamLength": 47.2, "teamWidth": 42.8, "compactness": 18.4,
        "defenseMidfieldGap": 21.4, "midfieldForwardGap": 16.8, "transitionSpeed": 4.6,
    },
)
