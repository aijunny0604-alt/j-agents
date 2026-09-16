"""PCM WAV 파일을 인수 순서대로 분석한다. 원본 오디오는 변경하지 않는다."""

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys
import wave


def analyze(paths):
    tracks = []
    elapsed = Fraction(0)
    formats = set()
    for index, path in enumerate(paths, 1):
        with wave.open(str(path), "rb") as source:
            rate = source.getframerate()
            frames = source.getnframes()
            channels = source.getnchannels()
            width = source.getsampwidth()
            if source.getcomptype() != "NONE" or rate <= 0 or frames <= 0:
                raise ValueError(f"분석할 수 없는 PCM WAV: {path}")
            # 잘린 데이터 청크를 정상 길이로 보고하지 않는다.
            remaining = frames
            while remaining:
                count = min(remaining, 65536)
                data = source.readframes(count)
                if len(data) != count * channels * width:
                    raise ValueError(f"오디오 데이터가 잘린 WAV: {path}")
                remaining -= count
        duration = Fraction(frames, rate)
        formats.add((rate, channels, width))
        tracks.append({
            "index": index, "title": path.stem, "file": path.name,
            "sample_rate": rate, "sample_frames": frames,
            "channels": channels, "sample_width_bytes": width,
            "start_seconds": float(elapsed),
            "duration_seconds": float(duration),
            "end_seconds": float(elapsed + duration),
            "start_exact": str(elapsed), "duration_exact": str(duration),
        })
        elapsed += duration
    return {
        "schema_version": 1, "order": "command_line",
        "total_seconds": float(elapsed), "total_exact": str(elapsed),
        "matching_pcm_formats": len(formats) == 1,
        "tracks": tracks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        # 잘못 지정한 경로로 원본을 덮어쓰지 않게 한다.
        if args.output.resolve() in {p.resolve() for p in args.files}:
            raise ValueError("출력 경로를 원본 WAV와 다르게 지정하세요.")
        manifest = analyze(args.files)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        # 기존 출력은 덮어쓰지 않는다. 필요한 경우 새 이름으로 실행한다.
        with args.output.open("x", encoding="utf-8") as target:
            json.dump(manifest, target, ensure_ascii=False, indent=2)
            target.write("\n")
    except (OSError, EOFError, wave.Error, ValueError) as error:
        print(f"분석 실패: {error}", file=sys.stderr)
        return 1
    print(f"{len(manifest['tracks'])}곡 / {manifest['total_seconds']:.6f}초 → {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
