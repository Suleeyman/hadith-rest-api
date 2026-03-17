from http import HTTPStatus

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_read_main() -> None:
    response = client.get("/")
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data == {
        "title": "Multilingual REST API of Popular Hadith Editions — Hadislam",
        "github_url": "https://github.com/Suleeyman/hadislam.org",
        "support": "https://ko-fi.com/ysuleyman",
        "swagger": "/docs",
        "redocly": "/redoc",
    }
