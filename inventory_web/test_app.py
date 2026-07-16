from __future__ import annotations

import importlib


def load_app(tmp_path, monkeypatch):
    monkeypatch.setenv("INVENTORY_DB", str(tmp_path / "inventory.db"))
    monkeypatch.setenv("RDK_VOICE_ENABLED", "0")
    import inventory_web.app as module

    return importlib.reload(module)


def test_robot_completion_updates_inventory_and_threshold(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    client = module.app.test_client()

    oreo = client.post(
        "/api/tasks/retrieval-complete", json={"item_id": 2, "task_id": "oreo-01"}
    ).get_json()
    assert oreo["items"][1]["quantity"] == 4
    assert oreo["alert_triggered"] is False

    coffee = client.post(
        "/api/tasks/retrieval-complete", json={"item_id": 1, "task_id": "coffee-01"}
    ).get_json()
    assert coffee["items"][0]["quantity"] == 6
    assert coffee["alert_triggered"] is True

    duplicate = client.post(
        "/api/tasks/retrieval-complete", json={"item_id": 1, "task_id": "coffee-01"}
    ).get_json()
    assert duplicate["duplicate"] is True
    assert duplicate["items"][0]["quantity"] == 6


def test_demo_reset_restores_initial_state(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    client = module.app.test_client()
    client.post("/api/items/1/adjust", json={"delta": -1})
    response = client.post("/api/demo/reset").get_json()
    assert [(item["quantity"], item["threshold"]) for item in response["items"]] == [(7, 6), (5, 2)]
