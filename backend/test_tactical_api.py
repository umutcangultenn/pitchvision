#!/usr/bin/env python3
"""
Tactical Analytics API standalone test.
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.tactical_analytics import router

# Create a simple FastAPI app for testing
app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/tactical/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "tactical-analytics"
    print("✅ Health endpoint test passed")

def test_config_endpoint():
    """Test config endpoint."""
    response = client.get("/api/tactical/config")
    assert response.status_code == 200
    data = response.json()
    assert "thresholds" in data
    assert "field_dimensions" in data
    print("✅ Config endpoint test passed")

def test_example_analysis():
    """Test example analysis endpoint."""
    response = client.post("/api/tactical/example-analysis")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "analysis" in data
    print("✅ Example analysis test passed")

def test_frame_analysis():
    """Test frame analysis endpoint."""
    test_data = {
        "match_id": 1,
        "timestamp": 1200.0,
        "players": [
            {
                "player_id": 1,
                "team_id": 1,
                "role": "defender",
                "x": 20.0,
                "y": 25.0,
                "speed": 3.5
            },
            {
                "player_id": 2,
                "team_id": 1,
                "role": "midfielder",
                "x": 40.0,
                "y": 30.0,
                "speed": 4.0
            },
            {
                "player_id": 3,
                "team_id": 2,
                "role": "forward",
                "x": 60.0,
                "y": 35.0,
                "speed": 5.0
            }
        ],
        "ball_position": [45.0, 30.0]
    }
    
    response = client.post("/api/tactical/analyze-frame", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "match_id" in data
    assert "teams" in data
    print("✅ Frame analysis test passed")

def test_validate_data():
    """Test data validation endpoint."""
    test_players = [
        {
            "player_id": 1,
            "team_id": 1,
            "role": "defender",
            "x": 20.0,
            "y": 25.0,
            "speed": 3.5
        }
    ]
    
    response = client.post("/api/tactical/validate-data", json=test_players)
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data
    assert "player_count" in data
    print("✅ Data validation test passed")

def main():
    """Run all tests."""
    print("PitchVision Tactical Analytics API Test")
    print("=" * 50)
    
    try:
        test_health_endpoint()
        test_config_endpoint()
        test_example_analysis()
        test_frame_analysis()
        test_validate_data()
        
        print("\n" + "=" * 50)
        print("✅ All API tests passed!")
        print("\nTactical Analytics API is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)