from __future__ import annotations

import json
import os
import queue
import shlex
import sqlite3
import subprocess
import threading
from contextlib import closing
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("INVENTORY_DB", BASE_DIR / "inventory.db"))
BOARD_HOST = os.getenv("RDK_BOARD_HOST", "sunrise@192.168.127.10")
BOARD_SPEAK = os.getenv(
    "RDK_BOARD_SPEAK",
    "MAGICBOXCTL_ROOT=/home/sunrise/.magicclaw /home/sunrise/openclaw_magicbox/bin/magicboxctl speak",
)
VOICE_ENABLED = os.getenv("RDK_VOICE_ENABLED", "1") == "1"
VOICE_LANGUAGE = os.getenv("RDK_VOICE_LANGUAGE", "zh").lower()

INITIAL_ITEMS = [
    (1, "雀巢咖啡", "Nestle coffee", 7, 6, "条", "stick"),
    (2, "奥利奥饼干", "Oreo cookie", 5, 2, "个", "cookie"),
]

app = Flask(__name__)
subscribers: set[queue.Queue[str]] = set()
subscribers_lock = threading.Lock()


def connect_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect_db()) as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                name_en TEXT NOT NULL DEFAULT '',
                quantity INTEGER NOT NULL CHECK(quantity >= 0),
                threshold INTEGER NOT NULL CHECK(threshold >= 0),
                unit TEXT NOT NULL,
                unit_en TEXT NOT NULL DEFAULT 'unit',
                alert_active INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                delta INTEGER NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(item_id) REFERENCES items(id)
            );
            CREATE TABLE IF NOT EXISTS task_completions (
                task_id TEXT PRIMARY KEY,
                item_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(item_id) REFERENCES items(id)
            );
            """
        )
        columns = {row[1] for row in db.execute("PRAGMA table_info(items)")}
        if "name_en" not in columns:
            db.execute("ALTER TABLE items ADD COLUMN name_en TEXT NOT NULL DEFAULT ''")
        if "unit_en" not in columns:
            db.execute("ALTER TABLE items ADD COLUMN unit_en TEXT NOT NULL DEFAULT 'unit'")
        count = db.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        if count == 0:
            now = datetime.now().isoformat(timespec="seconds")
            db.executemany(
                "INSERT INTO items(id, name, name_en, quantity, threshold, unit, unit_en, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (*item, now) for item in INITIAL_ITEMS
                ],
            )
        else:
            for item_id, _, name_en, _, _, _, unit_en in INITIAL_ITEMS:
                db.execute(
                    "UPDATE items SET name_en = ?, unit_en = ? WHERE id = ? AND name_en = ''",
                    (name_en, unit_en, item_id),
                )
        db.commit()


def inventory_snapshot() -> dict:
    with closing(connect_db()) as db:
        rows = db.execute(
            "SELECT id, name, name_en, quantity, threshold, unit, unit_en, alert_active, updated_at "
            "FROM items ORDER BY id"
        ).fetchall()
    return {
        "items": [
            {
                **dict(row),
                "alert": row["quantity"] <= row["threshold"],
                "alert_active": bool(row["alert_active"]),
            }
            for row in rows
        ],
        "server_time": datetime.now().isoformat(timespec="seconds"),
    }


def publish_snapshot() -> None:
    payload = json.dumps(inventory_snapshot(), ensure_ascii=False)
    with subscribers_lock:
        stale = []
        for subscriber in subscribers:
            try:
                subscriber.put_nowait(payload)
            except queue.Full:
                stale.append(subscriber)
        for subscriber in stale:
            subscribers.discard(subscriber)


def speak_on_board(message: str) -> None:
    if not VOICE_ENABLED:
        app.logger.info("Voice disabled: %s", message)
        return

    def worker() -> None:
        remote = f"{BOARD_SPEAK} {shlex.quote(message)}"
        try:
            result = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=4",
                    BOARD_HOST,
                    remote,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=45,
                check=False,
            )
            if result.returncode:
                app.logger.warning("RDK voice failed (%s): %s", result.returncode, result.stderr.strip())
        except (OSError, subprocess.TimeoutExpired) as exc:
            app.logger.warning("RDK voice unavailable: %s", exc)

    threading.Thread(target=worker, name="rdk-voice", daemon=True).start()


def low_stock_message(row: sqlite3.Row, quantity: int) -> str:
    if VOICE_LANGUAGE == "en":
        unit = row["unit_en"] + ("s" if quantity != 1 else "")
        return (
            f"Low stock warning. {row['name_en']} has {quantity} {unit} remaining. "
            f"The threshold is {row['threshold']}. Please replenish it."
        )
    return (
        f"{row['name']}目前仅剩余{quantity}{row['unit']}，"
        f"阈值为{row['threshold']}{row['unit']}，需要购买。"
    )


def apply_delta(
    item_id: int, delta: int, source: str, task_id: str | None = None
) -> tuple[dict, bool, bool]:
    now = datetime.now().isoformat(timespec="seconds")
    duplicate = False
    entered_alert = False
    row = None
    quantity = 0
    with closing(connect_db()) as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            raise KeyError(item_id)
        if task_id:
            previous = db.execute(
                "SELECT item_id FROM task_completions WHERE task_id = ?", (task_id,)
            ).fetchone()
            if previous is not None:
                if previous["item_id"] != item_id:
                    raise ValueError("task_id already belongs to another item")
                duplicate = True
            else:
                db.execute(
                    "INSERT INTO task_completions(task_id, item_id, created_at) VALUES (?, ?, ?)",
                    (task_id, item_id, now),
                )
        if not duplicate:
            quantity = max(0, row["quantity"] + delta)
            actual_delta = quantity - row["quantity"]
            is_alert = quantity <= row["threshold"]
            entered_alert = is_alert and not bool(row["alert_active"])
            db.execute(
                "UPDATE items SET quantity = ?, alert_active = ?, updated_at = ? WHERE id = ?",
                (quantity, int(is_alert), now, item_id),
            )
            if actual_delta:
                db.execute(
                    "INSERT INTO events(item_id, delta, source, created_at) VALUES (?, ?, ?, ?)",
                    (item_id, actual_delta, source, now),
                )
        db.commit()
    if entered_alert:
        speak_on_board(low_stock_message(row, quantity))
    if not duplicate:
        publish_snapshot()
    return inventory_snapshot(), entered_alert, duplicate


@app.get("/")
def dashboard():
    return render_template("dashboard.html")


@app.get("/admin")
def admin():
    return render_template("admin.html")


@app.get("/api/items")
def get_items():
    return jsonify(inventory_snapshot())


@app.get("/api/events")
def event_stream():
    subscriber: queue.Queue[str] = queue.Queue(maxsize=10)
    with subscribers_lock:
        subscribers.add(subscriber)

    def generate():
        try:
            yield f"data: {json.dumps(inventory_snapshot(), ensure_ascii=False)}\n\n"
            while True:
                try:
                    yield f"data: {subscriber.get(timeout=15)}\n\n"
                except queue.Empty:
                    yield ": keep-alive\n\n"
        finally:
            with subscribers_lock:
                subscribers.discard(subscriber)

    return Response(generate(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache"})


@app.post("/api/items/<int:item_id>/adjust")
def adjust_item(item_id: int):
    body = request.get_json(silent=True) or {}
    try:
        delta = int(body.get("delta", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "delta must be an integer"}), 400
    if delta not in (-1, 1):
        return jsonify({"error": "delta must be -1 or 1"}), 400

    try:
        snapshot, _, _ = apply_delta(item_id, delta, str(body.get("source", "admin"))[:40])
    except KeyError:
        return jsonify({"error": "item not found"}), 404
    return jsonify(snapshot)


@app.post("/api/tasks/retrieval-complete")
def retrieval_complete():
    """Commit inventory only after the robot reports a completed delivery."""
    body = request.get_json(silent=True) or {}
    try:
        item_id = int(body["item_id"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "item_id is required"}), 400
    task_id = str(body.get("task_id", "untracked"))[:80]
    if not task_id or task_id == "untracked":
        return jsonify({"error": "task_id is required for idempotency"}), 400
    try:
        snapshot, alert_triggered, duplicate = apply_delta(
            item_id, -1, f"smolvla:{task_id}", task_id=task_id
        )
    except KeyError:
        return jsonify({"error": "item not found"}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    return jsonify(
        {
            "accepted": True,
            "duplicate": duplicate,
            "task_id": task_id,
            "alert_triggered": alert_triggered,
            **snapshot,
        }
    )


@app.post("/api/demo/reset")
def reset_demo():
    now = datetime.now().isoformat(timespec="seconds")
    with closing(connect_db()) as db:
        db.execute("BEGIN IMMEDIATE")
        for item_id, name, name_en, quantity, threshold, unit, unit_en in INITIAL_ITEMS:
            db.execute(
                "UPDATE items SET name=?, name_en=?, quantity=?, threshold=?, unit=?, unit_en=?, "
                "alert_active=0, updated_at=? WHERE id=?",
                (name, name_en, quantity, threshold, unit, unit_en, now, item_id),
            )
        db.execute("DELETE FROM events")
        db.execute("DELETE FROM task_completions")
        db.commit()
    publish_snapshot()
    return jsonify(inventory_snapshot())


@app.post("/api/items/<int:item_id>/settings")
def update_item(item_id: int):
    body = request.get_json(silent=True) or {}
    try:
        name = str(body["name"]).strip()
        threshold = int(body["threshold"])
        unit = str(body["unit"]).strip()
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "name, threshold and unit are required"}), 400
    if not name or not unit or threshold < 0:
        return jsonify({"error": "invalid item settings"}), 400

    now = datetime.now().isoformat(timespec="seconds")
    with closing(connect_db()) as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT quantity, alert_active, name_en, unit_en FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "item not found"}), 404
        is_alert = row["quantity"] <= threshold
        entered_alert = is_alert and not bool(row["alert_active"])
        db.execute(
            "UPDATE items SET name = ?, threshold = ?, unit = ?, alert_active = ?, updated_at = ? WHERE id = ?",
            (name, threshold, unit, int(is_alert), now, item_id),
        )
        db.commit()

    if entered_alert:
        updated = dict(row)
        updated.update({"name": name, "threshold": threshold, "unit": unit})
        speak_on_board(low_stock_message(updated, row["quantity"]))
    publish_snapshot()
    return jsonify(inventory_snapshot())


@app.post("/api/voice/test")
def test_voice():
    body = request.get_json(silent=True) or {}
    message = str(body.get("message", "库存语音提醒测试成功。"))[:120]
    speak_on_board(message)
    return jsonify({"queued": True, "message": message})


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8088")), threaded=True)
