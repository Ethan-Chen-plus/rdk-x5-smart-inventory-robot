from __future__ import annotations

import argparse
import importlib
import json
import math
import platform
import sys
import time
import uuid
from pathlib import Path

import cv2
import numpy as np
import requests
import serial
import torch
from lerobot.common.control_utils import predict_action
from lerobot.policies import make_pre_post_processors
from lerobot.policies.smolvla import SmolVLAPolicy


CONFIRMATION = "RUN SMOLVLA ROBOT"


def load_config(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def import_xcore(root: str):
    root_path = Path(root).resolve()
    if not root_path.exists():
        raise FileNotFoundError(f"xCoreSDK root does not exist: {root_path}")
    for candidate in (root_path, root_path / "Release", root_path / "Release" / "windows"):
        sys.path.insert(0, str(candidate))
    module_name = "Release.windows.xCoreSDK_python" if platform.system() == "Windows" else "Release.linux.xCoreSDK_python"
    return importlib.import_module(module_name)


def ec_ok(ec: dict) -> bool:
    return int(ec.get("ec", 0)) == 0


def enum_int(value) -> int:
    return int(getattr(value, "value", value))


def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for value in data:
        crc ^= value
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


class Lmg90:
    def __init__(self, port: str, slave: int, force: int):
        self.serial = serial.Serial(port, 115200, bytesize=8, parity="N", stopbits=1, timeout=0.5)
        self.slave = slave
        self.write_register(0x9C41, force)

    def write_register(self, register: int, value: int) -> None:
        body = (
            bytes((self.slave, 0x10))
            + register.to_bytes(2, "big")
            + bytes((0x00, 0x01, 0x02))
            + int(value).to_bytes(2, "big")
        )
        frame = body + crc16(body).to_bytes(2, "little")
        self.serial.reset_input_buffer()
        self.serial.write(frame)
        response = self.serial.read(8)
        expected_body = bytes((self.slave, 0x10)) + register.to_bytes(2, "big") + bytes((0x00, 0x01))
        expected = expected_body + crc16(expected_body).to_bytes(2, "little")
        if response != expected:
            raise RuntimeError(f"LMG90 Modbus write failed: {response.hex()}")

    def command(self, width_percent: float) -> None:
        self.write_register(0x9C40, max(0, min(100, round(width_percent))))

    def close(self) -> None:
        self.serial.close()


class RokaeController:
    def __init__(self, cfg: dict, execute: bool):
        self.cfg = cfg
        self.execute = execute
        self.sdk = import_xcore(cfg["xcore_sdk_root"])
        robot_class = getattr(self.sdk, "xMateErProRobot", None) or self.sdk.xMateRobot
        self.robot = robot_class(cfg["robot_ip"])
        self.gripper = None
        self.check_ready()
        if execute:
            ec = {}
            self.robot.moveReset(ec)
            self.robot.setMotionControlMode(self.sdk.MotionControlMode.NrtCommandMode, ec)
            if not ec_ok(ec):
                raise RuntimeError(f"Unable to enter NrtCommandMode: {ec}")
            self.gripper = Lmg90(
                cfg["gripper_port"], int(cfg.get("gripper_slave", 1)), int(cfg["gripper_force_percent"])
            )

    def check_ready(self) -> None:
        ec = {}
        power = enum_int(self.robot.powerState(ec))
        operate = enum_int(self.robot.operateMode(ec))
        if not ec_ok(ec):
            raise RuntimeError(f"Unable to read ROKAE state: {ec}")
        print(f"ROKAE state: operate_mode={operate}, power_state={power}")
        if self.execute and operate != 1:
            raise RuntimeError("Robot must already be in automatic mode. Set it in RobotAssist.")
        if self.execute and power != 0:
            raise RuntimeError("Robot servo power must already be ON through the external enable/RobotAssist.")

    def state(self) -> np.ndarray:
        ec = {}
        joints = np.asarray(self.robot.jointPos(ec), dtype=np.float32)[:7]
        if not ec_ok(ec) or joints.shape != (7,):
            raise RuntimeError(f"Unable to read seven robot joints: {ec}")
        return joints

    def apply(self, action: np.ndarray) -> np.ndarray:
        if action.shape[0] < 8:
            raise ValueError(f"Expected 8-D action (7 joints + gripper), got {action.shape}")
        current = self.state()
        target = action[:7].astype(float)
        limits = [(math.radians(lo), math.radians(hi)) for lo, hi in self.cfg["joint_limits_deg"]]
        max_step = math.radians(float(self.cfg["max_joint_step_deg"]))
        target = np.asarray(
            [max(lo, min(hi, max(now - max_step, min(now + max_step, goal)))) for now, goal, (lo, hi) in zip(current, target, limits)],
            dtype=float,
        )
        gripper_width = float(max(0, min(100, action[7])))
        if not self.execute:
            print(json.dumps({"dry_run_joint_rad": target.tolist(), "gripper_percent": gripper_width}))
            return np.append(target, gripper_width)

        ec = {}
        cmd = self.sdk.MoveAbsJCommand(target.tolist(), float(self.cfg["move_speed"]), float(self.cfg["move_zone"]))
        cmd_id = self.sdk.PyString()
        self.robot.moveAppend(cmd, cmd_id, ec)
        if not ec_ok(ec):
            raise RuntimeError(f"moveAppend failed: {ec}")
        self.robot.moveStart(ec)
        if not ec_ok(ec):
            raise RuntimeError(f"moveStart failed: {ec}")
        self.gripper.command(gripper_width)
        deadline = time.monotonic() + 5.0
        time.sleep(0.02)
        while time.monotonic() < deadline:
            motion_ec = {}
            if enum_int(self.robot.operationState(motion_ec)) == 0:
                break
            time.sleep(0.02)
        else:
            raise TimeoutError("ROKAE command did not return to idle within 5 seconds")
        self.robot.moveReset(ec)
        if not ec_ok(ec):
            raise RuntimeError(f"moveReset after policy step failed: {ec}")
        return np.append(target, gripper_width)

    def stop(self) -> None:
        if self.execute:
            ec = {}
            self.robot.stop(ec)
            self.robot.moveReset(ec)
        if self.gripper:
            self.gripper.close()


def open_cameras(cfg: dict) -> list[cv2.VideoCapture]:
    cameras = []
    try:
        for index in cfg["camera_indices"]:
            camera = cv2.VideoCapture(
                index, cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_ANY
            )
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, cfg["frame_width"])
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg["frame_height"])
            if not camera.isOpened():
                camera.release()
                raise RuntimeError(f"Unable to open camera {index}")
            cameras.append(camera)
    except Exception:
        for camera in cameras:
            camera.release()
        raise
    return cameras


def read_observation(cameras, camera_keys, arm: RokaeController) -> dict[str, np.ndarray]:
    observation = {"observation.state": arm.state()}
    for camera, key in zip(cameras, camera_keys):
        ok, frame = camera.read()
        if not ok:
            raise RuntimeError(f"Camera read failed for {key}")
        observation[key] = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return observation


def notify_inventory(cfg: dict, task_id: str) -> dict:
    response = requests.post(
        f"{cfg['inventory_url'].rstrip('/')}/api/tasks/retrieval-complete",
        json={"item_id": int(cfg["item_id"]), "task_id": task_id},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the trained TuntunClaw SmolVLA policy on ROKAE xMate ER3 Pro.")
    parser.add_argument("--config", default="smolvla/config.json")
    parser.add_argument("--execute", action="store_true", help="Enable physical motion after safety confirmation.")
    parser.add_argument("--item-id", type=int, default=0, help="Override inventory item ID for this retrieval.")
    args = parser.parse_args()
    cfg = load_config(args.config)
    if args.item_id:
        cfg["item_id"] = args.item_id
    if args.execute:
        print("Clear the workspace. Keep the J5 pendant and emergency stop within reach.")
        if input(f"Type {CONFIRMATION!r} to enable model-controlled motion: ").strip() != CONFIRMATION:
            raise SystemExit("Cancelled.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = cfg["checkpoint"]
    policy = SmolVLAPolicy.from_pretrained(checkpoint).to(device).eval()
    preprocessor, postprocessor = make_pre_post_processors(
        policy.config,
        checkpoint,
        preprocessor_overrides={"device_processor": {"device": str(device)}},
    )
    arm = RokaeController(cfg, args.execute)
    cameras = []
    task_id = str(uuid.uuid4())
    close_seen = False
    delivered = False
    period = 1.0 / float(cfg["control_hz"])

    try:
        cameras = open_cameras(cfg)
        for step in range(int(cfg["max_steps"])):
            started = time.perf_counter()
            observation = read_observation(cameras, cfg["camera_keys"], arm)
            action = predict_action(
                observation,
                policy,
                device,
                preprocessor,
                postprocessor,
                use_amp=device.type == "cuda",
                task=cfg["task"],
                robot_type="rokae_xmate_er3_pro_lmg90",
            ).squeeze(0).cpu().numpy()
            applied = arm.apply(action)
            gripper = float(applied[7])
            close_seen = close_seen or gripper <= float(cfg["gripper_closed_threshold"])
            if close_seen and gripper >= float(cfg["gripper_open_threshold"]):
                result = notify_inventory(cfg, task_id)
                print(f"Delivery complete; inventory response: {json.dumps(result, ensure_ascii=False)}")
                delivered = True
                break
            elapsed = time.perf_counter() - started
            print(f"step={step + 1} inference_and_control={elapsed * 1000:.1f}ms")
            time.sleep(max(0.0, period - elapsed))
    except KeyboardInterrupt:
        print("Manual stop requested.")
    finally:
        arm.stop()
        for camera in cameras:
            camera.release()
    if not delivered:
        print("No completed close-then-open delivery was observed; inventory was not changed.")


if __name__ == "__main__":
    main()
