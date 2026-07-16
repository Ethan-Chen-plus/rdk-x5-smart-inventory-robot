from __future__ import annotations

import importlib


def load_app(tmp_path, monkeypatch):
    monkeypatch.setenv("INVENTORY_DB", str(tmp_path / "inventory.db"))
    monkeypatch.setenv("RDK_VOICE_ENABLED", "0")
    import inventory_web.app as module

    return importlib.reload(module)


def complete_verified_task(client, item_id, task_id, baseline, after):
    assert client.post(
        "/api/tasks/retrieval-start", json={"item_id": item_id, "task_id": task_id}
    ).status_code == 201
    assert client.post(
        f"/api/tasks/{task_id}/vision-baseline",
        json={"destination_occupancy": baseline, "frame_count": 15, "confidence": 0.9},
    ).status_code == 200
    candidate = client.post(
        "/api/tasks/retrieval-candidate", json={"task_id": task_id}
    ).get_json()
    assert candidate["status"] == "awaiting_vision"
    return client.post(
        f"/api/tasks/{task_id}/vision-confirm",
        json={"destination_occupancy": after, "frame_count": 15, "confidence": 0.9},
    )


def test_rdk_verified_delivery_updates_inventory_and_threshold(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    client = module.app.test_client()

    oreo = complete_verified_task(client, 2, "oreo-01", 0.0, 0.1062).get_json()
    assert oreo["items"][1]["quantity"] == 4
    assert oreo["alert_triggered"] is False

    coffee = complete_verified_task(client, 1, "coffee-01", 0.1062, 0.2720).get_json()
    assert coffee["items"][0]["quantity"] == 6
    assert coffee["alert_triggered"] is True

    duplicate = client.post(
        "/api/tasks/coffee-01/vision-confirm",
        json={"destination_occupancy": 0.2720, "frame_count": 15, "confidence": 0.9},
    ).get_json()
    assert duplicate["duplicate"] is True
    assert duplicate["items"][0]["quantity"] == 6


def test_arm_candidate_without_visual_change_does_not_update_inventory(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    client = module.app.test_client()

    response = complete_verified_task(client, 2, "empty-grasp", 0.0, 0.01)
    assert response.status_code == 422
    assert response.get_json()["task"]["status"] == "vision_rejected"
    assert client.get("/api/items").get_json()["items"][1]["quantity"] == 5


def test_legacy_arm_only_completion_is_rejected(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    client = module.app.test_client()
    response = client.post(
        "/api/tasks/retrieval-complete", json={"item_id": 2, "task_id": "unsafe"}
    )
    assert response.status_code == 410


def test_demo_reset_restores_initial_state(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    client = module.app.test_client()
    client.post("/api/items/1/adjust", json={"delta": -1})
    response = client.post("/api/demo/reset").get_json()
    assert [(item["quantity"], item["threshold"]) for item in response["items"]] == [(7, 6), (5, 2)]
