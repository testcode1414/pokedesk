from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app


client = TestClient(app)

mock_pokemon = {
    "name": "pikachu",
    "sprites": {"front_default": "img_url"},
    "types": [{"type": {"name": "electric"}}],
    "stats": [
        {"stat": {"name": "speed"}, "base_stat": 90}
    ],
    "abilities": [
        {"ability": {"name": "static"}}
    ]
}



@patch("main.requests.get")
def test_featured_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_pokemon

    response = client.get("/featured")

    assert response.status_code == 200

    data = response.json()

    assert  isinstance(data,list)

    assert len(data) > 0

    first = data[0]

    assert first['name'] == "Pikachu"
    assert first['image'] == "img_url"
    assert first["types"] == ["electric"]
    assert first["stats"]["speed"] == 90
    assert first["abilities"] == ["static"]
