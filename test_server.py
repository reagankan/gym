import json
import os
import pytest
from server import app

IMGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs")


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_index_returns_200_with_gym_tracker(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Gym Tracker" in resp.data


def test_api_exercises_returns_json_list(client):
    resp = client.get("/api/exercises")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(f.endswith(".png") for f in data)


def test_serve_existing_image(client):
    existing = sorted(f for f in os.listdir(IMGS_DIR) if f.endswith(".png"))[0]
    resp = client.get(f"/imgs/{existing}")
    assert resp.status_code == 200


def test_serve_nonexistent_image_returns_404(client):
    resp = client.get("/imgs/nonexistent_file_xyz.png")
    assert resp.status_code == 404


def test_process_cache_generates_plots(client):
    """POST /api/process-cache returns 200 now that plot_utils saves with .png extension."""
    resp = client.post("/api/process-cache")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "status" in data
    assert "Generated plots" in data["status"]


def test_update_cache_fails_on_linux(client):
    """macnotesapp stub now raises ImportError; server catches it and returns 500."""
    resp = client.post("/api/update-cache")
    assert resp.status_code == 500
    data = resp.get_json()
    assert "error" in data
    assert "macnotesapp" in data["error"].lower()


def test_index_contains_is_mac_false_on_linux(client):
    """On Linux, the rendered HTML should set isMac = false."""
    resp = client.get("/")
    assert b"isMac = false" in resp.data


def test_index_has_btn_update(client):
    """The index page should contain the btn-update button."""
    resp = client.get("/")
    assert b'id="btn-update"' in resp.data


def test_process_cache_stream_returns_sse(client):
    """POST /api/process-cache-stream returns 200 with text/event-stream."""
    resp = client.post("/api/process-cache-stream")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.content_type


def test_process_cache_stream_has_data_lines(client):
    """The SSE response body contains data: lines."""
    resp = client.post("/api/process-cache-stream")
    assert b"data:" in resp.data


def test_process_cache_stream_last_event_done(client):
    """The last SSE data event should have 'done': true."""
    resp = client.post("/api/process-cache-stream")
    lines = [l for l in resp.data.decode().splitlines() if l.startswith("data:")]
    assert len(lines) > 0
    last = json.loads(lines[-1].removeprefix("data:").strip())
    assert last.get("done") is True
