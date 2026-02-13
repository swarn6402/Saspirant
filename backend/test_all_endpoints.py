from datetime import datetime

import requests

API_BASE = "http://127.0.0.1:5000"


def test_endpoints():
    """Test all API endpoints."""
    print("=" * 60)
    print("TESTING ALL API ENDPOINTS")
    print("=" * 60)

    print("\n1. Testing health check...")
    response = requests.get(f"{API_BASE}/api/health", timeout=20)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("   [OK] Health check passed")

    print("\n2. Testing routes list...")
    response = requests.get(f"{API_BASE}/api/routes", timeout=20)
    print(f"   Status: {response.status_code}")
    routes = response.json()
    print(f"   Total routes: {len(routes)}")
    print("   [OK] Routes listed")

    print("\n3. Testing user registration...")
    test_email = f"test_{datetime.now().timestamp()}@example.com"
    user_data = {
        "name": "Test User",
        "email": test_email,
        "date_of_birth": "2000-01-01",
        "highest_qualification": "Graduate",
    }
    response = requests.post(f"{API_BASE}/api/auth/register", json=user_data, timeout=20)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    user_id = response.json().get("user_id")
    assert response.status_code == 201
    print(f"   [OK] User registered with ID: {user_id}")

    print("\n4. Testing get user...")
    response = requests.get(f"{API_BASE}/api/auth/user/{user_id}", timeout=20)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    print("   [OK] User retrieved")

    print("\n5. Testing add preferences...")
    prefs_data = {
        "exam_categories": ["UPSC", "SSC"],
        "min_age": 21,
        "max_age": 35,
        "preferred_locations": ["All India"],
    }
    response = requests.post(f"{API_BASE}/api/preferences/{user_id}", json=prefs_data, timeout=20)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    print("   [OK] Preferences added")

    print("\n6. Testing get preferences...")
    response = requests.get(f"{API_BASE}/api/preferences/{user_id}", timeout=20)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    print("   [OK] Preferences retrieved")

    print("\n7. Testing add monitored URL...")
    url_data = {
        "url": "https://upsc.gov.in/examinations/active",
        "website_name": "UPSC Official",
        "scraper_type": "html",
    }
    response = requests.post(
        f"{API_BASE}/api/preferences/{user_id}/urls", json=url_data, timeout=30
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 201
    print("   [OK] URL added")

    print("\n8. Testing dashboard summary...")
    response = requests.get(f"{API_BASE}/api/dashboard/{user_id}/summary", timeout=20)
    print(f"   Status: {response.status_code}")
    summary = response.json()
    print(f"   User: {summary['user']['name']}")
    print(f"   Stats: {summary['stats']}")
    print(f"   Recent alerts: {len(summary['recent_alerts'])}")
    assert response.status_code == 200
    print("   [OK] Dashboard loaded")

    print("\n9. Testing alerts list...")
    response = requests.get(f"{API_BASE}/api/dashboard/{user_id}/alerts", timeout=20)
    print(f"   Status: {response.status_code}")
    alerts_data = response.json()
    print(f"   Total alerts: {alerts_data['total']}")
    print(f"   Current page: {alerts_data['page']}")
    assert response.status_code == 200
    print("   [OK] Alerts retrieved")

    print("\n" + "=" * 60)
    print("[OK] ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    test_endpoints()
