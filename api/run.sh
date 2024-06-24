#!/bin/bash

set -euxo pipefail

# python3 init.py
# make migrate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
