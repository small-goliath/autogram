#!/bin/bash

WATCH_FILE="./kakaotalk/KakaoTalk_latest.txt"
source .venv/bin/activate

inotifywait -m -e create,modify "${WATCH_FILE}" | while read FILE
do
    pip install -r requirements.txt
    python3 -m app.batch.kakaotalk_active_verify
    python3 -m app.batch.kakaotalk_active
done