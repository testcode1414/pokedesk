from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app

client = TestClient(app)


@patch("main.requests.post")
def test_analyze_success(mock_post):

    mock_post.return_value.json.return_value = {
    "candidates": [{
            "content": {
                "parts": [{
                    "text": '{"summary":"fast attacker","strong_against":["water"],"weak_against":["ground"],"battle_tip":"use speed","first_appearance":"pokemon red"}'
                }]
            }
        }]
    }

    payload = {
        "name": "Pikachu",
        "image": "img",
        "types": ["electric"],
        "stats": {"speed": 90},
        "abilities": ["static"]
    }

    response = client.post("/analyse", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data
    assert data["summary"] == "fast attacker"
    assert "strong_against" in data
    assert "weak_against" in data