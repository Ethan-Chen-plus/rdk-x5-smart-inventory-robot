#!/usr/bin/env python3
"""Confirm deliveries from the Magic Box WebSocket camera stream."""

from __future__ import annotations

import argparse
import json
import logging
import time
import urllib.error
import urllib.request
from collections import deque
from pathlib import Path

import cv2
import numpy as np
from websockets.exceptions import WebSocketException
from websockets.sync.client import connect

from roi_transfer_verifier import crop_image, measure_occupancy, parse_polygon, parse_roi


LOG = logging.getLogger("rdk_roi_verifier")


def request_json(method: str, url: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def websocket_message_to_bgr(message: bytes) -> np.ndarray:
    start = message.find(b"\xff\xd8")
    end = message.rfind(b"\xff\xd9")
    if start < 0 or end <= start:
        raise ValueError("Magic Box WebSocket frame does not contain a JPEG image")
    image = cv2.imdecode(np.frombuffer(message[start : end + 2], dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode Magic Box WebSocket JPEG")
    return image


class RdkRoiVerifier:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.api = config["inventory_url"].rstrip("/")
        self.roi = parse_roi(config["roi"])
        self.polygon = parse_polygon(config["polygon"])
        self.sample_frames = int(config.get("sample_frames", 15))
        self.settle_seconds = float(config.get("settle_seconds", 2.0))
        self.max_spread = float(config.get("max_occupancy_spread", 0.02))
        self.pixel_threshold = int(config.get("pixel_threshold", 28))
        self.minimum_component_area = int(config.get("minimum_component_area", 80))
        self.reference = crop_image(Path(config["empty_reference_image"]), self.roi)
        self.samples: deque[tuple[float, float]] = deque(maxlen=self.sample_frames * 3)
        self.active_key: tuple[str, str] | None = None
        self.active_since = time.monotonic()
        self.last_poll = 0.0

    def observe(self, image: np.ndarray) -> None:
        x, y, width, height = self.roi
        current = image[y : y + height, x : x + width]
        if current.shape != self.reference.shape:
            raise ValueError(f"ROI produced {current.shape}; expected {self.reference.shape}")
        occupancy, _, _ = measure_occupancy(
            self.reference,
            current,
            self.polygon,
            self.pixel_threshold,
            self.minimum_component_area,
        )
        self.samples.append((time.monotonic(), occupancy))

    def stable_observation(self) -> tuple[float, float] | None:
        earliest = self.active_since + self.settle_seconds
        values = [value for observed_at, value in self.samples if observed_at >= earliest]
        if len(values) < self.sample_frames:
            return None
        values = values[-self.sample_frames :]
        occupancy = float(np.median(values))
        spread = float(np.percentile(values, 90) - np.percentile(values, 10))
        confidence = max(0.0, min(1.0, 1.0 - spread / self.max_spread))
        return occupancy, confidence

    def poll_task(self) -> None:
        now = time.monotonic()
        if now - self.last_poll < float(self.config.get("api_poll_seconds", 0.5)):
            return
        self.last_poll = now
        try:
            tasks = request_json("GET", f"{self.api}/api/tasks/active")["tasks"]
        except (OSError, urllib.error.URLError, ValueError, KeyError) as exc:
            LOG.warning("inventory API unavailable: %s", exc)
            return
        if not tasks:
            self.active_key = None
            return

        task = tasks[0]
        key = (task["task_id"], task["status"])
        if key != self.active_key:
            self.active_key = key
            self.active_since = time.monotonic()
            self.samples.clear()
            LOG.info("collecting %s frames for task %s", key[1], key[0])
            return
        observation = self.stable_observation()
        if observation is None:
            return
        occupancy, confidence = observation
        endpoint = "vision-baseline" if task["status"] == "awaiting_baseline" else "vision-confirm"
        payload = {
            "destination_occupancy": round(occupancy, 6),
            "frame_count": self.sample_frames,
            "confidence": round(confidence, 6),
        }
        try:
            result = request_json(
                "POST", f"{self.api}/api/tasks/{task['task_id']}/{endpoint}", payload
            )
            LOG.info(
                "submitted %s: occupancy=%.4f confidence=%.3f status=%s",
                endpoint,
                occupancy,
                confidence,
                result.get("status") or result.get("task", {}).get("status"),
            )
            self.active_key = None
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            LOG.error("%s rejected (%s): %s", endpoint, exc.code, body)

    def run(self) -> None:
        reconnect_delay = float(self.config.get("websocket_reconnect_seconds", 2.0))
        while True:
            try:
                with connect(
                    self.config.get("websocket_url", "ws://127.0.0.1:8080"),
                    open_timeout=5,
                ) as socket:
                    socket.send(
                        json.dumps(
                            {"filter_prefix": self.config.get("filter_prefix", "null/null/null")}
                        )
                    )
                    LOG.info("connected to Magic Box camera WebSocket")
                    while True:
                        message = socket.recv()
                        if isinstance(message, str):
                            continue
                        self.observe(websocket_message_to_bgr(message))
                        self.poll_task()
            except (OSError, ValueError, WebSocketException) as exc:
                LOG.warning("camera WebSocket unavailable: %s", exc)
                time.sleep(reconnect_delay)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    RdkRoiVerifier(config).run()


if __name__ == "__main__":
    main()
