#!/bin/bash

set -xe

# python3 init.py
# make migrate
# exec uvicorn main:app --reload --host 0.0.0.0 --port 8000  --log-config conf/logging.json
# exec gunicorn -c ${GUNICORN_CONFIG_FILE} app.main:app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
