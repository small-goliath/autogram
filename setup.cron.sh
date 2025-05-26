#!/bin/bash

ROOT_PATH="$HOME/autogram"
APP_PATH="app.batchauto_active"
LOG_PATH="$ROOT_PATH/logs/crontab.log"
PYTHON_PATH=".venv/bin/python"
CRON_BACKUP="$ROOT_PATH/backup/crontab_backup_$(date +%Y%m%d%H%M%S).txt"

crontab -l > "$CRON_BACKUP"

CRON="00 09 * * * cd $ROOT_PATH && $PYTHON_PATH $APP_PATH >> $LOG_PATH 2>&1"

(crontab -l; echo "$CRON") | sort -u | crontab -

echo "✅ 크론탭이 설정되었습니다."
echo "🔍 백업된 기존 크론탭: $CRON_BACKUP"
echo "📂 로그 파일 위치: $LOG_PATH"

crontab -l
