#!/bin/bash

set -euxo pipefail

# python3 init.py
# make migrate
# export IMAGEIO_FFMPEG_EXE=~/Downloads/ffmpeg
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
