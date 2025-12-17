# Release Notes

## v0.1.0 — Initial Release

**mp4-to-mp3** — MP4 / M4V / MOV to MP3 converter using ffmpeg.

---

### ✨ Features

* Convert **MP4 / M4V / MOV** files to **MP3** using `ffmpeg`
* Interactive CLI:

  * Choose **CBR** or **VBR** encoding
  * Optional **recursive directory scanning**
* **Auto-detection** of audio streams via `ffprobe`

  * Sensible default encoding selection
  * Graceful skipping of video-only files
* Multiple execution modes:

  * Standalone script: `python mp4_to_mp3.py`
  * Module execution: `python -m mp4_to_mp3`
  * Installed CLI: `mp4-to-mp3` (via `pipx`)
* Optional **Makefile** for convenience workflows
* Metadata preservation where possible

---

### 🧠 Smart Defaults

* Defaults to **VBR encoding** for typical AAC sources
* Uses **stream copy** when input audio is already MP3 (no re-encode)
* Robust handling of edge cases (e.g. missing audio streams)

---

### 🛠 Technical Details

* Python **>= 3.9**
* External dependency: **ffmpeg / ffprobe** (installed separately, e.g. via Homebrew)
* No mandatory Python dependencies (standard library only)
* Clean project structure with:

  * `pyproject.toml`
  * `__main__.py` for module execution
  * Single source of truth for versioning

---

### 🧪 CLI Improvements

* Fully featured `--help` output with grouped options and examples
* `--version` flag
* Clear error messages and safe skip logic

---

### ⚠️ Known Limitations

* `ffmpeg` must be installed separately (not bundled)
* Only the first audio stream is used if multiple streams are present
* No progress indicator yet

---

### 🔜 Planned

* Proper exit codes for automation and scripting
* Progress indicator for long-running conversions
* Optional shell autocompletion
* CI pipeline and automated releases

---

