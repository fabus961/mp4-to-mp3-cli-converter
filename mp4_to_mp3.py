#!/usr/bin/env python3
import argparse
import shutil
import subprocess
from pathlib import Path

VIDEO_EXTS = {".mp4", ".m4v", ".mov"}

def ask_choice(prompt: str, choices: dict, default_key: str):
    """choices: {'c': 'CBR', 'v': 'VBR'} returns key"""
    options = "/".join([f"{k}={v}" for k, v in choices.items()])
    default_label = choices[default_key]
    while True:
        raw = input(f"{prompt} ({options}) [Default: {default_key}={default_label}]: ").strip().lower()
        if raw == "":
            return default_key
        if raw in choices:
            return raw
        print(f"Bitte eingeben: {', '.join(choices.keys())} (oder Enter für Default).")

def ask_yes_no(prompt: str, default: bool):
    d = "y" if default else "n"
    while True:
        raw = input(f"{prompt} (y/n) [Default: {d}]: ").strip().lower()
        if raw == "":
            return default
        if raw in {"y", "yes", "j", "ja"}:
            return True
        if raw in {"n", "no", "nein"}:
            return False
        print("Bitte y/n eingeben (oder Enter für Default).")

def ensure_ffmpeg():
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg nicht gefunden. Installiere es mit: brew install ffmpeg")

def run_ffmpeg(input_path: Path, output_path: Path, overwrite: bool, mode: str, bitrate: str, vbr_q: int) -> None:
    ensure_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-i", str(input_path),
        "-vn",
        "-c:a", "libmp3lame",
        "-map_metadata", "0",
    ]

    if mode == "cbr":
        cmd += ["-b:a", bitrate]
    else:
        # VBR: q=0..9 (0 beste Qualität / größte Datei)
        cmd += ["-q:a", str(vbr_q)]

    cmd.append("-y" if overwrite else "-n")
    cmd.append(str(output_path))

    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise SystemExit(f"Konvertierung fehlgeschlagen: {input_path}")

def iter_inputs(in_path: Path, recursive: bool):
    if in_path.is_dir():
        if recursive:
            yield from (p for p in in_path.rglob("*") if p.suffix.lower() in VIDEO_EXTS)
        else:
            yield from (p for p in in_path.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS)
    else:
        yield in_path

def main():
    p = argparse.ArgumentParser(description="MP4 -> MP3 Konverter (macOS/M1, via ffmpeg) mit interaktiven Prompts")
    p.add_argument("input", help="MP4-Datei oder Ordner")
    p.add_argument("-o", "--out", help="Ausgabeordner (optional)")
    p.add_argument("--overwrite", action="store_true", help="Vorhandene MP3s überschreiben")
    p.add_argument("--mode", choices=["cbr", "vbr"], help="CBR oder VBR (wenn nicht gesetzt, wird gefragt)")
    p.add_argument("-b", "--bitrate", default="192k", help="CBR Bitrate (default: 192k)")
    p.add_argument("--vbr-q", type=int, default=2, help="VBR Qualität 0..9 (default: 2)")
    p.add_argument("--recursive", action="store_true", help="Unterordner rekursiv durchsuchen (wenn nicht gesetzt, wird ggf. gefragt)")
    args = p.parse_args()

    in_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve() if args.out else None

    if not in_path.exists():
        raise SystemExit(f"Pfad nicht gefunden: {in_path}")

    # 1) Mode fragen, wenn nicht per CLI gesetzt
    mode = args.mode
    if mode is None:
        choice = ask_choice(
            "Willst du CBR oder VBR encoden?",
            choices={"c": "CBR (feste Bitrate)", "v": "VBR (variable Bitrate)"},
            default_key="v",
        )
        mode = "cbr" if choice == "c" else "vbr"

    # 2) Rekursiv fragen, wenn input ein Ordner ist und Flag nicht gesetzt
    recursive = args.recursive
    if in_path.is_dir() and not args.recursive:
        recursive = ask_yes_no("Soll ich Unterordner rekursiv durchsuchen?", default=True)

    # Validierung VBR-q
    if mode == "vbr" and not (0 <= args.vbr_q <= 9):
        raise SystemExit("--vbr-q muss zwischen 0 und 9 liegen.")

    # Dateien sammeln
    files = sorted(iter_inputs(in_path, recursive=recursive))
    files = [f for f in files if f.is_file() and f.suffix.lower() in VIDEO_EXTS]

    if not files:
        raise SystemExit(f"Keine MP4/M4V/MOV Dateien gefunden in: {in_path}")

    for f in files:
        target_dir = out_dir if out_dir else f.parent
        out_file = target_dir / (f.stem + ".mp3")

        if out_file.exists() and not args.overwrite:
            print(f"Überspringe (existiert): {out_file}")
            continue

        print(f"Konvertiere: {f} -> {out_file} [{mode.upper()}]")
        run_ffmpeg(
            input_path=f,
            output_path=out_file,
            overwrite=args.overwrite,
            mode=mode,
            bitrate=args.bitrate,
            vbr_q=args.vbr_q,
        )
        print("OK")

if __name__ == "__main__":
    main()
