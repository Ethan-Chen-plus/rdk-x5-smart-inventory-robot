from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts


VOICE_SEGMENTS = [
    (0.0, 12.0, "Hello. This is TuntunClaw, our memory-aware household inventory and manipulation assistant, developed with OpenClaw and RDK X5."),
    (12.0, 32.0, "The first natural-language instruction asks the robot to move the chocolate onto the plate. OpenClaw parses the task, while the vision-language model and S A M identify and segment the target and destination."),
    (32.0, 51.0, "GraspNet estimates a valid grasp pose, and the simulated arm completes the first pick and place. The next instruction asks it to move the apple into the basket."),
    (51.0, 72.0, "The scene is not reset between tasks. Object poses and inventory state persist, so the second action starts from the real result of the first action instead of a fresh simulation."),
    (72.0, 89.0, "OpenClaw runs perception and planning again, distinguishes the apple from its destination container, selects a free placement region, and completes the task."),
    (89.0, 108.0, "Inventory memory records every movement. When an item reaches its threshold, the system sends a replenishment notification and updates the structured household supply table."),
    (108.0, 115.5, "The Magic Box supports live spoken inventory queries. The following exchange preserves the original user and device audio."),
    (168.0, 185.0, "Now we move to the real-world experiment. The system uses an RDK X5 Magic Box, a ROKAE xMate E R 3 Pro seven-axis arm, an L M G 90 gripper, two live camera views, and a tablet dashboard."),
    (185.0, 206.0, "The project team completed Smol V L A fine-tuning and deployed the trained policy on an NVIDIA R T X Pro 6000 GPU with 96 gigabytes of memory. Live images, current joint state, and the language instruction generate online robot actions; this is not trajectory replay."),
    (206.0, 228.0, "RDK X5 simultaneously provides edge perception and speech. Its Bayes B P U sustained 30.02 frames per second, with 24.61 milliseconds average inference latency across 644 samples."),
    (228.0, 253.0, "The initial inventory is five Oreo cookies with a threshold of two, and seven Nestle coffee sticks with a threshold of six. The robot first releases one Oreo into the delivery tray."),
    (253.0, 274.0, "A successful gripper close followed by release commits the delivery. Oreo inventory changes from five to four. Four remains above the threshold of two, so no low-stock warning is issued."),
    (274.0, 302.0, "The trained policy continues with the coffee retrieval. Model outputs pass through conservative joint limits, a maximum two-degree change per control step, and the ROKAE xCore S D K safety interface."),
    (302.0, 323.0, "After the coffee stick is released, the inventory service writes the event to SQLite and immediately updates the tablet through server-sent events. Coffee changes from seven to six."),
    (323.0, 329.0, "At the configured threshold, the system now triggers the Magic Box replenishment warning."),
]


SUBTITLE_SEGMENTS = [
    *VOICE_SEGMENTS[:7],
    (115.5, 121.08, "User: Hello, hello."),
    (121.08, 125.86, "User: Which three supplies currently have the lowest remaining quantities?"),
    (143.08, 147.35, "Magic Box: Two remain, one above the threshold. Stored in the balcony cabinet."),
    (147.35, 151.95, "Magic Box: Apples: three remain, one above the threshold. Stored on the kitchen shelf."),
    (151.95, 156.01, "Magic Box: Toothpaste: four remain, two above the threshold. Stored in the bathroom cabinet."),
    (156.01, 159.89, "User: Send me a purchase link for the toothpaste. Thank you."),
    (159.89, 168.0, "The request is sent through Feishu, completing the spoken inventory interaction."),
    *VOICE_SEGMENTS[7:],
    (329.0, 344.1, "Magic Box: Nestle coffee has six sticks remaining. The threshold is six. Replenishment is required."),
]


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


async def synthesize(folder: Path) -> list[Path]:
    clips = []
    for index, (start, end, text) in enumerate(VOICE_SEGMENTS):
        raw = folder / f"raw_{index:02}.mp3"
        await edge_tts.Communicate(text, "en-US-AriaNeural", rate="+5%").save(str(raw))
        clip = folder / f"clip_{index:02}.m4a"
        available = end - start - 0.15
        source_duration = duration(raw)
        filters = []
        if source_duration > available:
            filters.append(f"atempo={source_duration / available:.6f}")
        filters.append("loudnorm=I=-18:LRA=7:TP=-2")
        run(
            [
                "ffmpeg", "-loglevel", "error", "-y", "-i", str(raw),
                "-af", ",".join(filters), "-t", f"{available:.3f}", "-c:a", "aac", "-b:a", "160k", str(clip),
            ]
        )
        clips.append(clip)
    return clips


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    folder = output_path.parent / f"{output_path.stem}_voice"
    folder.mkdir(parents=True, exist_ok=True)

    clips = asyncio.run(synthesize(folder))
    video_duration = duration(input_path)
    command = [
        "ffmpeg", "-loglevel", "error", "-y", "-i", str(input_path),
        "-f", "lavfi", "-t", f"{video_duration:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
    ]
    for clip in clips:
        command.extend(["-i", str(clip)])
    filters = ["[1:a]volume=0[base]"]
    mix_inputs = ["[base]"]
    for index, (start, _, _) in enumerate(VOICE_SEGMENTS):
        input_index = index + 2
        label = f"v{index}"
        delay = round(start * 1000)
        filters.append(f"[{input_index}:a]adelay={delay}|{delay}[{label}]")
        mix_inputs.append(f"[{label}]")
    filters.append(
        "".join(mix_inputs)
        + f"amix=inputs={len(mix_inputs)}:duration=longest:normalize=0,atrim=0:{video_duration:.3f}[narration]"
    )
    filters.extend(
        [
            "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=3[dialogue_src][ambient_src][alert_src]",
            "[dialogue_src]atrim=start=115.5:end=168,asetpts=PTS-STARTPTS,highpass=f=80,lowpass=f=12000,loudnorm=I=-17:LRA=9:TP=-2,adelay=115500|115500[dialogue]",
            "[ambient_src]atrim=start=168:end=329,asetpts=PTS-STARTPTS,volume=0.25,adelay=168000|168000[ambient]",
            "[alert_src]atrim=start=329:end=344.1,asetpts=PTS-STARTPTS,highpass=f=80,lowpass=f=12000,loudnorm=I=-13:LRA=7:TP=-1.5,adelay=329000|329000[alert]",
            f"[narration][dialogue][ambient][alert]amix=inputs=4:duration=longest:normalize=0,alimiter=limit=0.95,atrim=0:{video_duration:.3f}[dub]",
        ]
    )
    command.extend(
        [
            "-filter_complex", ";".join(filters), "-map", "0:v:0", "-map", "[dub]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", str(output_path),
        ]
    )
    run(command)

    subtitle_path = output_path.with_suffix(".en.srt")
    subtitle_path.write_text(
        "\n\n".join(
            f"{index}\n{timestamp(start)} --> {timestamp(end)}\n{text}"
            for index, (start, end, text) in enumerate(SUBTITLE_SEGMENTS, 1)
        )
        + "\n",
        encoding="utf-8",
    )
    print(output_path)
    print(subtitle_path)


if __name__ == "__main__":
    main()
