"""
Tactical Analytics Engine kullanım örneği.
Gerçek maç verisi ile nasıl kullanılacağını gösterir.
"""
import numpy as np
from typing import List
from .types import TrackPoint, PlayerRole, TacticalConfig
from .team_shape import calculate_team_shape, calculate_block_gaps
from .defensive_line import detect_defensive_line_break
from .transitions import analyze_team_transition
from .alerts_new import generate_tactical_alerts, filter_alerts_by_priority
from .player_scores import calculate_tactical_score, calculate_physical_score
from .drill_mapping import get_drill_recommendations, create_training_session


def create_sample_tracking_data() -> List[TrackPoint]:
    """
    Örnek tracking verisi oluşturur.
    Gerçek uygulamada bu veri video analiz sisteminden gelir.
    """
    tracking_data = []
    timestamp = 1200.0  # 20. dakika
    
    # Takım 1 (Ev sahibi) - 4-3-3 formasyonu
    team1_positions = [
        # Kaleci
        (1, 8, 34, PlayerRole.GOALKEEPER),
        # Savunma
        (2, 18, 15, PlayerRole.DEFENDER),
        (3, 20, 25, PlayerRole.DEFENDER),
        (4, 19, 43, PlayerRole.DEFENDER),
        (5, 17, 53, PlayerRole.DEFENDER),
        # Orta saha
        (6, 35, 20, PlayerRole.MIDFIELDER),
        (7, 38, 34, PlayerRole.MIDFIELDER),
        (8, 36, 48, PlayerRole.MIDFIELDER),
        # Forvet
        (9, 55, 15, PlayerRole.FORWARD),
        (10, 58, 34, PlayerRole.FORWARD),
        (11, 56, 53, PlayerRole.FORWARD),
    ]
    
    # Takım 2 (Deplasman) - 4-4-2 formasyonu
    team2_positions = [
        # Kaleci
        (12, 97, 34, PlayerRole.GOALKEEPER),
        # Savunma
        (13, 87, 15, PlayerRole.DEFENDER),
        (14, 85, 25, PlayerRole.DEFENDER),
        (15, 86, 43, PlayerRole.DEFENDER),
        (16, 88, 53, PlayerRole.DEFENDER),
        # Orta saha
        (17, 70, 18, PlayerRole.MIDFIELDER),
        (18, 72, 28, PlayerRole.MIDFIELDER),
        (19, 71, 40, PlayerRole.MIDFIELDER),
        (20, 69, 50, PlayerRole.MIDFIELDER),
        # Forvet
        (21, 50, 25, PlayerRole.FORWARD),
        (22, 52, 43, PlayerRole.FORWARD),
    ]
    
    # TrackPoint objelerini oluştur
    for player_id, x, y, role in team1_positions:
        # Rastgele hız ekle
        speed = np.random.uniform(0.5, 6.0)
        vx = np.random.uniform(-2.0, 2.0)
        vy = np.random.uniform(-1.0, 1.0)
        
        point = TrackPoint(
            player_id=player_id,
            team_id=1,
            role=role,
            timestamp=timestamp,
            x=x,
            y=y,
            speed=speed,
            vx=vx,
            vy=vy
        )
        tracking_data.append(point)
    
    for player_id, x, y, role in team2_positions:
        speed = np.random.uniform(0.5, 6.0)
        vx = np.random.uniform(-2.0, 2.0)
        vy = np.random.uniform(-1.0, 1.0)
        
        point = TrackPoint(
            player_id=player_id,
            team_id=2,
            role=role,
            timestamp=timestamp,
            x=x,
            y=y,
            speed=speed,
            vx=vx,
            vy=vy
        )
        tracking_data.append(point)
    
    return tracking_data


def analyze_match_moment(tracking_data: List[TrackPoint], team_id: int = 1):
    """
    Belirli bir maç anını analiz eder.
    
    Args:
        tracking_data: Oyuncu tracking verileri
        team_id: Analiz edilecek takım ID'si
    """
    print(f"=== Takım {team_id} Analizi ===")
    
    # Takım oyuncularını filtrele
    team_players = [p for p in tracking_data if p.team_id == team_id]
    
    # 1. Takım şekli analizi
    print("\n1. Takım Şekli Analizi:")
    team_shape = calculate_team_shape(team_players)
    print(f"   Takım Boyu: {team_shape.team_length:.1f}m")
    print(f"   Takım Genişliği: {team_shape.team_width:.1f}m")
    print(f"   Kompaktlık: {team_shape.compactness:.1f}m")
    print(f"   Merkez Nokta: ({team_shape.centroid_x:.1f}, {team_shape.centroid_y:.1f})")
    
    # 2. Blok mesafeleri
    print("\n2. Blok Mesafeleri:")
    block_gaps = calculate_block_gaps(team_players)
    print(f"   Savunma-Orta Saha: {block_gaps.defensive_midfield_gap:.1f}m")
    print(f"   Orta Saha-Forvet: {block_gaps.midfield_forward_gap:.1f}m")
    
    # 3. Savunma hattı analizi
    print("\n3. Savunma Hattı Analizi:")
    defenders = [p for p in team_players if p.role == PlayerRole.DEFENDER]
    if len(defenders) >= 3:
        defensive_alert = detect_defensive_line_break(defenders)
        if defensive_alert:
            print(f"   ⚠️ UYARI: {defensive_alert.description}")
            print(f"   Güven: {defensive_alert.confidence:.2f}")
            print(f"   Önem: {defensive_alert.severity.value}")
        else:
            print("   ✅ Savunma hattı düzgün")
    
    # 4. Taktiksel uyarılar
    print("\n4. Taktiksel Uyarılar:")
    alerts = generate_tactical_alerts(
        tracking_data, 
        team_id=team_id, 
        timestamp=tracking_data[0].timestamp,
        ball_position=(45.0, 30.0)  # Örnek top pozisyonu
    )
    
    if alerts:
        for i, alert in enumerate(alerts, 1):
            print(f"   {i}. {alert.alert_type.value.upper()}")
            print(f"      {alert.description}")
            print(f"      Güven: {alert.confidence:.2f} | Önem: {alert.severity.value}")
    else:
        print("   ✅ Taktiksel uyarı yok")
    
    # 5. Oyuncu performans skorları
    print("\n5. Oyuncu Performans Örnekleri:")
    sample_players = team_players[:3]  # İlk 3 oyuncu
    
    for player in sample_players:
        # Basit skor hesaplama (gerçekte zaman serisi gerekli)
        player_history = [player]  # Tek frame örneği
        team_positions = [p for p in team_players if p.player_id != player.player_id]
        opponent_positions = [p for p in tracking_data if p.team_id != team_id]
        
        tactical_score = calculate_tactical_score(
            player_history, team_positions, opponent_positions
        )
        physical_score = calculate_physical_score(player_history)
        
        print(f"   Oyuncu #{player.player_id} ({player.role.value})")
        print(f"      Taktiksel: {tactical_score:.1f}/10")
        print(f"      Fiziksel: {physical_score:.1f}/10")
    
    # 6. Antrenman önerileri
    if alerts:
        print("\n6. Antrenman Önerileri:")
        for alert in alerts[:2]:  # İlk 2 uyarı için
            recommendations = get_drill_recommendations(
                alert, team_level="youth", available_time=30, player_count=11
            )
            
            if recommendations:
                drill = recommendations[0]
                print(f"   Uyarı: {alert.alert_type.value}")
                print(f"   Önerilen Drill: {drill.name}")
                print(f"   Süre: {drill.duration_minutes} dk | Zorluk: {drill.difficulty}")
                print(f"   Odak: {', '.join(drill.focus_areas)}")


def create_full_training_session_example():
    """Tam antrenman seansı oluşturma örneği."""
    print("\n=== Antrenman Seansı Oluşturma ===")
    
    # Örnek uyarılar oluştur
    tracking_data = create_sample_tracking_data()
    alerts = generate_tactical_alerts(
        tracking_data, team_id=1, timestamp=1200.0, ball_position=(45.0, 30.0)
    )
    
    if alerts:
        session = create_training_session(
            alerts=alerts,
            session_duration=90,
            team_level="youth",
            player_count=16
        )
        
        print(f"Toplam Süre: {session['total_duration']} dakika")
        print(f"Gerçek Süre: {session['actual_duration']} dakika")
        
        print("\nIsınma:")
        for activity in session['warm_up']['activities']:
            print(f"  - {activity}")
        
        print(f"\nAna Driller ({len(session['main_drills'])} adet):")
        for i, drill_info in enumerate(session['main_drills'], 1):
            drill = drill_info['drill']
            print(f"  {i}. {drill['name']} ({drill['duration']} dk)")
            print(f"     Problem: {drill_info['alert_description']}")
            print(f"     Odak: {', '.join(drill['focus_areas'])}")
            print(f"     Zorluk: {drill['difficulty']} | Oyuncu: {drill['player_count']}")
        
        print("\nSoğuma:")
        for activity in session['cool_down']['activities']:
            print(f"  - {activity}")


def main():
    """Ana örnek fonksiyon."""
    print("PitchVision Tactical Analytics Engine - Kullanım Örneği")
    print("=" * 60)
    
    # Örnek tracking verisi oluştur
    tracking_data = create_sample_tracking_data()
    print(f"Oluşturulan veri: {len(tracking_data)} oyuncu pozisyonu")
    
    # Her iki takım için analiz yap
    analyze_match_moment(tracking_data, team_id=1)
    print("\n" + "=" * 60)
    analyze_match_moment(tracking_data, team_id=2)
    
    # Antrenman seansı örneği
    print("\n" + "=" * 60)
    create_full_training_session_example()


if __name__ == "__main__":
    main()