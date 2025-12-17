import sys
import pathlib
from urllib.parse import quote

# Ensure src is on path so we can import the FastAPI app
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    encoded = quote(activity, safe="")
    email = "tester@example.com"

    # Ensure clean state: remove test email if already present
    resp = client.get("/activities")
    participants = resp.json().get(activity, {}).get("participants", [])
    if email in participants:
        client.delete(f"/activities/{encoded}/participants", params={"email": email})

    # Sign up
    resp = client.post(f"/activities/{encoded}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant present
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{encoded}/participants", params={"email": email})
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Verify participant removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]
