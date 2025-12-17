# Makefile for MP4 -> MP3 converter (Python venv + ffmpeg)
# Usage examples:
#   make setup
#   make convert IN="~/Downloads/video.mp4"
#   make convert IN="~/Downloads/mp4s" OUT="~/Music/mp3" OVERWRITE=1

VENV := .venv
PY   := $(VENV)/bin/python
PIP  := $(VENV)/bin/pip

SCRIPT := mp4_to_mp3.py

# Optional params
IN ?=
OUT ?=
MODE ?=
BITRATE ?= 192k
VBRQ ?= 2
RECURSIVE ?=
OVERWRITE ?=

.PHONY: help setup venv deps check-ffmpeg convert clean

help:
	@echo "Targets:"
	@echo "  make setup                 -> creates venv + installs deps (if any)"
	@echo "  make convert IN=...         -> converts a file or folder"
	@echo "  make clean                  -> removes venv + caches"
	@echo ""
	@echo "Options for convert:"
	@echo "  IN=path        (required)  input file or folder"
	@echo "  OUT=path       (optional)  output folder"
	@echo "  MODE=cbr|vbr    (optional)  if omitted, script will ask"
	@echo "  BITRATE=192k    (optional)  CBR bitrate"
	@echo "  VBRQ=2          (optional)  VBR quality 0..9 (0 best)"
	@echo "  RECURSIVE=1     (optional)  recursive folder scan"
	@echo "  OVERWRITE=1     (optional)  overwrite existing mp3 files"

setup: check-ffmpeg venv deps

check-ffmpeg:
	@command -v ffmpeg >/dev/null 2>&1 || (echo "ffmpeg not found. Install: brew install ffmpeg" && exit 1)

venv:
	@test -d "$(VENV)" || python3 -m venv "$(VENV)"
	@$(PIP) -q install --upgrade pip >/dev/null

deps:
	@if [ -f requirements.txt ]; then \
		$(PIP) -q install -r requirements.txt; \
	else \
		echo "No requirements.txt found (that's fine)."; \
	fi

convert: check-ffmpeg venv deps
	@if [ -z "$(IN)" ]; then \
		echo "ERROR: IN is required. Example: make convert IN=\"~/Downloads/video.mp4\""; \
		exit 1; \
	fi
	@ARGS=""; \
	if [ -n "$(OUT)" ]; then ARGS="$$ARGS -o \"$(OUT)\""; fi; \
	if [ -n "$(MODE)" ]; then ARGS="$$ARGS --mode $(MODE)"; fi; \
	if [ -n "$(BITRATE)" ]; then ARGS="$$ARGS -b $(BITRATE)"; fi; \
	if [ -n "$(VBRQ)" ]; then ARGS="$$ARGS --vbr-q $(VBRQ)"; fi; \
	if [ -n "$(RECURSIVE)" ]; then ARGS="$$ARGS --recursive"; fi; \
	if [ -n "$(OVERWRITE)" ]; then ARGS="$$ARGS --overwrite"; fi; \
	eval "$(PY) $(SCRIPT) \"$(IN)\" $$ARGS"

clean:
	@rm -rf "$(VENV)" .pytest_cache __pycache__
	@echo "Cleaned."
