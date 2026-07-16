from __future__ import annotations

import argparse
import json
from pathlib import Path

from faster_whisper import WhisperModel


def timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("output")
    parser.add_argument("--model", default="large-v3-turbo")
    parser.add_argument("--language", default="zh")
    args = parser.parse_args()

    model = WhisperModel(args.model, device="cuda", compute_type="float16")
    segments, info = model.transcribe(
        args.video,
        language=args.language,
        vad_filter=True,
        word_timestamps=False,
        beam_size=5,
    )
    rows = [
        {"start": segment.start, "end": segment.end, "text": segment.text.strip()}
        for segment in segments
        if segment.text.strip()
    ]
    output = Path(args.output)
    output.write_text(
        json.dumps({"language": info.language, "duration": info.duration, "segments": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    srt = output.with_suffix(".zh.srt")
    srt.write_text(
        "\n\n".join(
            f"{index}\n{timestamp(row['start'])} --> {timestamp(row['end'])}\n{row['text']}"
            for index, row in enumerate(rows, 1)
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"segments={len(rows)} language={info.language} duration={info.duration:.2f}s")


if __name__ == "__main__":
    main()
