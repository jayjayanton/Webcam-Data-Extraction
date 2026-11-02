"""Capture JPEG frames from authorized live streams with Streamlink and FFmpeg."""
from __future__ import annotations
import argparse
import csv
import re
import subprocess
from pathlib import Path
import streamlink

def safe_name(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", s).strip("_")[:70] or "stream"

def load_feeds(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    if path.suffix.lower() in (".xlsx", ".xls"):
        import pandas as pd
        return pd.read_excel(path).fillna("").to_dict("records")
    raise ValueError("Feed list must be CSV or XLSX")

def capture(name: str, url: str, output: Path, frames: int, interval: float) -> None:
    streams = streamlink.streams(url)
    if not streams:
        raise ValueError("No playable streams discovered")
    stream = streams.get("best") or next(iter(streams.values()))
    stream_url = stream.to_url() if hasattr(stream, "to_url") else None
    if not stream_url:
        raise RuntimeError("No direct stream URL; source may need a different Streamlink handler")
    output.mkdir(parents=True, exist_ok=True)
    filename = str(output / (safe_name(name) + "_%03d.jpg"))
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", stream_url,
               "-vf", f"fps=1/{interval}", "-frames:v", str(frames), "-q:v", "2", filename]
    subprocess.run(command, check=True, timeout=max(90, int(frames * interval * 4)))

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feeds", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/jackson_hole"))
    parser.add_argument("--frames", type=int, default=3)
    parser.add_argument("--interval", type=float, default=15.0)
    args = parser.parse_args()
    if args.frames < 1 or args.interval <= 0:
        parser.error("frames and interval must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "capture_log.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "url", "status"])
        writer.writeheader()
        for row in load_feeds(args.feeds):
            name, url = str(row.get("Name", "")).strip(), str(row.get("Link", "")).strip()
            if not name or not url:
                writer.writerow({"name": name, "url": url, "status": "missing Name or Link"})
                continue
            try:
                capture(name, url, args.output_dir / safe_name(name), args.frames, args.interval)
                status = "captured"
            except Exception as exc:
                status = f"error: {exc}"
            writer.writerow({"name": name, "url": url, "status": status})
            print(f"{name}: {status}")

if __name__ == "__main__":
    main()
