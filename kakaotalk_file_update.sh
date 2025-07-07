#!/bin/bash

WATCH_FILE="/home/sch/autogram/kakaotalk/KakaoTalk_latest.txt"
cd /home/sch/autogram
source .venv/bin/activate

inotifywait -m -e create,modify "${WATCH_FILE}" | while read FILE
do
    pip install -r requirements.txt
    echo "kakaotalk file update!!!"
    date
    python3 -m app.batch.kakaotalk_active_verify
    python3 -m app.batch.kakaotalk_active
done
