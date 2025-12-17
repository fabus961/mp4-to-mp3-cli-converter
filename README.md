# MP4 → MP3 Converter (macOS / Apple Silicon M1)

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![macOS](https://img.shields.io/badge/macOS-Apple%20Silicon%20M1-black)
![ffmpeg](https://img.shields.io/badge/ffmpeg-required-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

A small Python-based tool to convert **MP4 / M4V / MOV** files to **MP3** using `ffmpeg`.

The script is **interactive by default** and will ask you:

* whether you want **CBR or VBR** encoding
* whether subfolders should be **scanned recursively** (when the input is a directory)

Technically this performs: **demux → decode → MP3 encode**.

---

## Demo / Usage Preview

```text
$ make convert IN="~/Downloads/mp4s"

? CBR or VBR? [Default: VBR]
> v

? Scan subfolders recursively? [Y/n]
> y

Converting: intro.mp4  -> intro.mp3  [VBR]
OK
Converting: talk.mp4   -> talk.mp3   [VBR]
OK
```

---

## Requirements

### 1) ffmpeg (system dependency)

`ffmpeg` is a native binary (not a pure Python package) and should be installed via Homebrew:

```bash
brew install ffmpeg
```

Verify installation:

```bash
ffmpeg -version
```

### 2) Python 3

macOS usually ships with Python 3. If not:

```bash
brew install python
```

---

## Project Structure

Place these files in one directory:

* `mp4_to_mp3.py`
* `Makefile`
* `requirements.txt` (optional)

> Note: The script uses only the Python standard library.
> A `requirements.txt` file is optional and can be empty.

Example `requirements.txt`:

```txt
# no Python dependencies required
```

---

## Setup (virtual environment)

Create a virtual environment and prepare everything:

```bash
make setup
```

This will:

* check for `ffmpeg`
* create `.venv`
* upgrade `pip`
* install dependencies from `requirements.txt` (if present)

---

## Usage

You can use this tool **with or without Makefile**.

---

### Usage via Makefile (recommended for convenience)

Single file:

```bash
make convert IN="~/Downloads/video.mp4"
```

Directory (interactive prompts):

```bash
make convert IN="~/Downloads/mp4s"
```

Non-interactive:

```bash
make convert IN="~/Downloads/mp4s" MODE=vbr VBRQ=2 RECURSIVE=1 OVERWRITE=1
```

---

### Usage without Makefile (plain Python)

Direct execution:

```bash
python3 mp4_to_mp3.py ~/Downloads/video.mp4
```

Directory:

```bash
python3 mp4_to_mp3.py ~/Downloads/mp4s
```

Make it executable:

```bash
chmod +x mp4_to_mp3.py
./mp4_to_mp3.py ~/Downloads/video.mp4
```

Install into PATH (optional):

```bash
mkdir -p ~/.local/bin
cp mp4_to_mp3.py ~/.local/bin/mp4-to-mp3
chmod +x ~/.local/bin/mp4-to-mp3
```

Then use anywhere:

```bash
mp4-to-mp3 ~/Downloads/mp4s
```

---

### CLI Help

```bash
mp4-to-mp3 --help
```

This prints all available options and flags.

---

### Encoding Auto-Detection

If you **do not specify `--mode`**, the tool will:

1. Inspect the input audio stream
2. Prefer **VBR** for typical AAC sources
3. Fall back to **CBR** if detection fails

You can always override this behavior using:

```bash
--mode cbr
--mode vbr
```

---

### pipx Installation (optional)

You can install this tool globally using `pipx`.

1. Install pipx (once):

```bash
brew install pipx
pipx ensurepath
```

2. From the project directory:

```bash
pipx install .
```

After that, you can use:

```bash
mp4-to-mp3 ~/Downloads/video.mp4
```

---

## Converting Files

### 1) Single file (interactive CBR/VBR prompt)

```bash
make convert IN="~/Downloads/video.mp4"
```

### 2) Directory (interactive prompts)

```bash
make convert IN="~/Downloads/mp4s"
```

You will be asked:

* CBR or VBR?
* Scan subfolders recursively?

---

### 3) Specify output directory

```bash
make convert IN="~/Downloads/mp4s" OUT="~/Music/mp3"
```

---

### 4) Non-interactive (all options via flags)

**VBR, quality 2, recursive, overwrite existing files:**

```bash
make convert IN="~/Downloads/mp4s" MODE=vbr VBRQ=2 RECURSIVE=1 OVERWRITE=1
```

**CBR, 192k bitrate:**

```bash
make convert IN="~/Downloads/mp4s" MODE=cbr BITRATE=192k
```

---

## Encoding Options (Quick Reference)

### CBR (Constant Bitrate)

* Fixed bitrate (e.g. `128k`, `192k`, `320k`)
* Predictable file size

### VBR (Variable Bitrate)

* Quality-based encoding
* Controlled via `VBRQ` (0–9)

| VBRQ | Quality             | File Size |
| ---- | ------------------- | --------- |
| 0    | best                | largest   |
| 2    | very good (default) | medium    |
| 4    | okay                | smaller   |

---

## Repository Structure (Recommended)

```text
mp4-to-mp3/
├── mp4_to_mp3.py        # main conversion script
├── Makefile             # build & run helpers
├── README.md             # documentation
├── requirements.txt      # optional Python deps
├── .gitignore
└── .venv/                # virtual environment (not committed)
```

Suggested `.gitignore`:

```gitignore
.venv/
__pycache__/
*.mp3
.DS_Store
```

---

## Cleanup

Remove the virtual environment and caches:

```bash
make clean
```

---

## Troubleshooting

### `ffmpeg not found`

Install it via Homebrew:

```bash
brew install ffmpeg
```

### Permission errors (macOS)

Make sure the terminal has access to the target directories:

* System Settings → Privacy & Security → Files and Folders

---

## License

Do whatever you want with it 🙂
