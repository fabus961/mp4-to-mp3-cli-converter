#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

VIDEO_EXTS = {".mp4", ".m4v", ".mov"}


@dataclass
class ProbeInfo:
    codec_name: Optional[str] = None
    bit_rate: Optional[int] = None
    channels: Optional[int] = None
    sample_rate: Optional[int] = None


def which_or_exit(cmd: str, install_hint: str) -> None:
    if shutil.which(cmd) is None:
        raise SystemExit(f"{cmd} not found. {install_hint}")


def ensure_tools() -> None:
    which_or_exit("ffmpeg", "Install via Homebrew: brew install ffmpeg")
    which_or_exit("ffprobe", "Install via Homebrew: brew install ffmpeg")


def ask_choice(prompt: str, choices: dict[str, str], default_key: str) -> str:
    options = "/".join([f"{k}={v}" for k, v in choices.items()])
    default_label = choices[default_key]
    while True:
        raw = input(f"{prompt} ({options}) [Default: {default_key}={default_label}]: ").strip().lower()
        if raw == "":
            return default_key
        if raw in choices:
            return raw
        print(f"Please enter one of: {', '.join(choices.keys())} (or press Enter for default).")


def ask_yes_no(prompt: str, default: bool) -> bool:
    d = "y" if default else "n"
    while True:
        raw = input(f"{prompt} (y/n) [Default: {d}]: ").strip().lower()
        if raw == "":
            return default
        if raw in {"y", "yes", "j", "ja"}:
            return True
        if raw in {"n", "no", "nein"}:
            return False
        print("Please enter y/n (or press Enter for default).")


def iter_inputs(in_path: Path, recursive: bool) -> Iterable[Path]:
    if in_path.is_dir():
        if recursive:
            yield from (p for p in in_path.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS)
        else:
            yield from (p for p in in_path.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS)
    else:
        yield in_path


def ffprobe_audio_info(path: Path) -> ProbeInfo:
    """
    Tries to read the first audio stream info using ffprobe JSON output.
    Returns ProbeInfo with None fields if something fails.
    """
    ensure_tools()
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,bit_rate,channels,sample_rate",
        "-of", "json",
        str(path),
    ]
    try:
        out = subprocess.check_output(cmd, text=True)
        data = json.loads(out)
        streams = data.get("streams") or []
        if not streams:
            return ProbeInfo()
        s = streams[0]
        return ProbeInfo(
            codec_name=s.get("codec_name"),
            bit_rate=int(s["bit_rate"]) if s.get("bit_rate") else None,
            channels=int(s["channels"]) if s.get("channels") else None,
            sample_rate=int(s["sample_rate"]) if s.get("sample_rate") else None,
        )
    except Exception:
        return ProbeInfo()


def autodetect_mode(path: Path) -> str:
    """
    Auto-detect strategy:
    - If codec is mp3: prefer 'copy' (no re-encode).
    - Otherwise: prefer 'vbr' (good default for typical AAC sources).
    - If detection fails: 'vbr'.
    """
    info = ffprobe_audio_info(path)
    codec = (info.codec_name or "").lower()

    if codec == "mp3":
        return "copy"
    if codec:
        return "vbr"
    return "vbr"

def has_audio_stream(path: Path) -> bool:
    ensure_tools()
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=index",
        "-of", "json",
        str(path),
    ]
    try:
        out = subprocess.check_output(cmd, text=True)
        data = json.loads(out)
        return bool(data.get("streams"))
    except Exception:
        return False

def run_ffmpeg(
    input_path: Path,
    output_path: Path,
    overwrite: bool,
    mode: str,
    bitrate: str,
    vbr_q: int,
) -> None:
    ensure_tools()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-i", str(input_path),
        "-vn",
        "-map", "0:a:0",
        "-map_metadata", "0",
    ]

    if mode == "copy":
        cmd += ["-c:a", "copy"]
    else:
        cmd += ["-c:a", "libmp3lame"]
        if mode == "cbr":
            cmd += ["-b:a", bitrate]
        elif mode == "vbr":
            cmd += ["-q:a", str(vbr_q)]
        else:
            raise SystemExit(f"Unknown mode: {mode}")

    cmd.append("-y" if overwrite else "-n")
    cmd.append(str(output_path))

    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise SystemExit(f"Conversion failed: {input_path}")


def build_parser() -> argparse.ArgumentParser:
    examples = r"""
Examples:
  mp4-to-mp3 ~/Downloads/video.mp4
  mp4-to-mp3 ~/Downloads/mp4s --recursive
  mp4-to-mp3 ~/Downloads/mp4s -o ~/Music/mp3 --mode vbr --vbr-q 2
  mp4-to-mp3 ~/Downloads/video.mp4 --mode cbr -b 192k
  mp4-to-mp3 ~/Downloads/video.mp4 --mode auto
"""
    p = argparse.ArgumentParser(
        prog="mp4-to-mp3",
        description="Convert MP4/M4V/MOV files to MP3 using ffmpeg (interactive prompts + auto-detect).",
        epilog=examples.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    io = p.add_argument_group("Input / Output")
    io.add_argument("input", help="Input file or directory (MP4/M4V/MOV)")
    io.add_argument("-o", "--out", help="Output directory (optional). Defaults to input file's directory.")

    enc = p.add_argument_group("Encoding")
    enc.add_argument(
        "--mode",
        choices=["auto", "cbr", "vbr", "copy"],
        default="auto",
        help="Encoding mode. 'auto' detects source via ffprobe. 'copy' attempts stream copy if already MP3.",
    )
    enc.add_argument("-b", "--bitrate", default="192k", help="CBR bitrate (e.g. 128k, 192k, 320k). Default: 192k.")
    enc.add_argument("--vbr-q", type=int, default=2, help="VBR quality 0..9 (0 best). Default: 2.")

    behavior = p.add_argument_group("Behavior")
    behavior.add_argument("--recursive", action="store_true", help="Scan subfolders recursively (when input is a directory).")
    behavior.add_argument("--overwrite", action="store_true", help="Overwrite existing MP3 files.")
    behavior.add_argument("--no-prompt", action="store_true", help="Disable interactive prompts (use defaults/flags only).")

    return p


def main() -> None:
    p = build_parser()
    args = p.parse_args()

    in_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve() if args.out else None

    if not in_path.exists():
        raise SystemExit(f"Path not found: {in_path}")

    if args.mode == "vbr" and not (0 <= args.vbr_q <= 9):
        raise SystemExit("--vbr-q must be between 0 and 9.")

    # Determine recursive behavior (interactive if directory and not set)
    recursive = args.recursive
    if in_path.is_dir() and not args.recursive and not args.no_prompt:
        recursive = ask_yes_no("Scan subfolders recursively?", default=True)

    files = sorted(iter_inputs(in_path, recursive=recursive))
    files = [f for f in files if f.is_file() and f.suffix.lower() in VIDEO_EXTS]

    if not files:
        raise SystemExit(f"No MP4/M4V/MOV files found in: {in_path}")

    # Determine mode
    mode = args.mode
    if mode == "auto":
        # If no prompts -> auto-detect per file
        if args.no_prompt:
            pass
        else:
            # Ask user whether to override auto-detect
            choice = ask_choice(
                "Encoding mode? (auto detects via ffprobe)",
                choices={"a": "AUTO", "c": "CBR", "v": "VBR"},
                default_key="a",
            )
            mode = {"a": "auto", "c": "cbr", "v": "vbr"}[choice]

    for f in files:
        target_dir = out_dir if out_dir else f.parent
        out_file = target_dir / (f.stem + ".mp3")

        if out_file.exists() and not args.overwrite:
            print(f"Skip (exists): {out_file}")
            continue

        file_mode = mode
        if file_mode == "auto":
            file_mode = autodetect_mode(f)

        print(f"Converting: {f} -> {out_file} [{file_mode.upper()}]")
        if not has_audio_stream(f):
            print(f"  No audio stream found, skipping.")
            continue

        run_ffmpeg(
            input_path=f,
            output_path=out_file,
            overwrite=args.overwrite,
            mode=file_mode,
            bitrate=args.bitrate,
            vbr_q=args.vbr_q,
        )
        print("OK")


if __name__ == "__main__":
    main()
