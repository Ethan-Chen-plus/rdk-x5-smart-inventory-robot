from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from lerobot.datasets import LeRobotDataset


TASK = "Pick the requested household supply and place it in the delivery tray."


def jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def nearest_state(states: list[dict], epoch_s: float) -> np.ndarray:
    row = min(states, key=lambda value: abs(value["monotonic_s"] - epoch_s))
    return np.asarray(row["robot"]["joint_rad"][:7], dtype=np.float32)


def open_video(path: Path) -> cv2.VideoCapture:
    video = cv2.VideoCapture(str(path))
    if not video.isOpened():
        raise RuntimeError(f"Unable to open {path}")
    return video


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert synchronized TuntunClaw recordings to LeRobot v3.")
    parser.add_argument("--episodes", required=True, help="Directory containing episode_* folders.")
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--root", default="outputs/datasets/tuntunclaw_rokae")
    parser.add_argument("--push-to-hub", action="store_true")
    args = parser.parse_args()

    features = {
        "observation.state": {
            "dtype": "float32",
            "shape": (7,),
            "names": [f"joint_{index + 1}_rad" for index in range(7)],
        },
        "action": {
            "dtype": "float32",
            "shape": (8,),
            "names": [f"joint_{index + 1}_rad" for index in range(7)] + ["gripper_width_percent"],
        },
        "observation.images.front": {
            "dtype": "video",
            "shape": (480, 640, 3),
            "names": ["height", "width", "channels"],
        },
        "observation.images.wrist": {
            "dtype": "video",
            "shape": (480, 640, 3),
            "names": ["height", "width", "channels"],
        },
    }
    dataset = LeRobotDataset.create(
        repo_id=args.repo_id,
        fps=6,
        features=features,
        robot_type="rokae_xmate_er3_pro_lmg90",
        root=Path(args.root),
        use_videos=True,
        image_writer_threads=4,
    )

    episode_dirs = sorted(Path(args.episodes).glob("episode_*"))
    if not episode_dirs:
        raise SystemExit("No episode_* folders found.")
    for episode in episode_dirs:
        sync = json.loads((episode / "cameras" / "synced_manifest.json").read_text(encoding="utf-8"))
        index = jsonl(episode / "cameras" / "synced_index.jsonl")
        states = jsonl(episode / "robot_state_force.jsonl")
        gripper = np.load(episode / "gripper_width_f32.npy").astype(np.float32)
        # Recording monotonic time and camera epoch share a fixed offset for the episode.
        first_epoch = index[0]["target_wall_time_epoch_s"]
        first_monotonic = states[0]["monotonic_s"]
        offset = first_monotonic - first_epoch
        front = open_video(Path(sync["videos"]["top_orbbec_rgb"]))
        wrist = open_video(Path(sync["videos"]["wrist_d435_rgb"]))
        try:
            frame_count = min(len(index), len(gripper))
            for frame_index in range(frame_count):
                ok_front, front_bgr = front.read()
                ok_wrist, wrist_bgr = wrist.read()
                if not ok_front or not ok_wrist:
                    raise RuntimeError(f"Video ended early in {episode.name} at frame {frame_index}")
                state = nearest_state(
                    states, index[frame_index]["target_wall_time_epoch_s"] + offset
                )
                action = np.append(state, gripper[frame_index]).astype(np.float32)
                dataset.add_frame(
                    {
                        "observation.state": state,
                        "observation.images.front": cv2.cvtColor(front_bgr, cv2.COLOR_BGR2RGB),
                        "observation.images.wrist": cv2.cvtColor(wrist_bgr, cv2.COLOR_BGR2RGB),
                        "action": action,
                        "task": TASK,
                    }
                )
            dataset.save_episode()
            print(f"Converted {episode.name}: {frame_count} frames")
        finally:
            front.release()
            wrist.release()

    dataset.finalize()
    if args.push_to_hub:
        dataset.push_to_hub()


if __name__ == "__main__":
    main()
