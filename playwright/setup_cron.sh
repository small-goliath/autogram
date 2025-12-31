#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
COLLECT_SCRIPT="$PROJECT_ROOT/playwright/collect_unfollowers.py"
LOG_DIR="$PROJECT_ROOT/logs"

mkdir -p "$LOG_DIR"

CRON_JOB="0 4 * * 1 cd $PROJECT_ROOT && $PYTHON_BIN $COLLECT_SCRIPT >> $LOG_DIR/unfollower_collection_\$(date +\\%Y\\%m\\%d_\\%H\\%M\\%S).log 2>&1"

echo "======================================"
echo "언팔로워 수집 Crontab 설정"
echo "======================================"
echo ""
echo "프로젝트 루트: $PROJECT_ROOT"
echo "Python 바이너리: $PYTHON_BIN"
echo "스크립트: $COLLECT_SCRIPT"
echo "로그 디렉토리: $LOG_DIR"
echo ""

if [ ! -f "$PYTHON_BIN" ]; then
    echo "오류: Python 바이너리를 찾을 수 없습니다: $PYTHON_BIN"
    echo "먼저 가상환경을 생성하세요: python3 -m venv .venv"
    exit 1
fi

if [ ! -f "$COLLECT_SCRIPT" ]; then
    echo "오류: 스크립트를 찾을 수 없습니다: $COLLECT_SCRIPT"
    exit 1
fi

if crontab -l 2>/dev/null | grep -F "collect_unfollowers.py" > /dev/null; then
    echo "collect_unfollowers.py에 대한 cron job이 이미 존재합니다!"
    echo ""
    echo "현재 등록된 crontab 항목:"
    crontab -l 2>/dev/null | grep "collect_unfollowers.py"
    echo ""
    read -p "기존 항목을 제거하고 다시 추가하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        crontab -l 2>/dev/null | grep -v "collect_unfollowers.py" | crontab -
        echo "기존 항목이 제거되었습니다."
    else
        echo "설정이 취소되었습니다."
        exit 0
    fi
fi

(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "✓ Cron job이 성공적으로 추가되었습니다!"
echo ""
echo "등록된 Cron job: $CRON_JOB"
echo ""
echo "스크립트는 매주 월요일 오전 4시에 실행됩니다"
echo ""
echo "확인하려면 다음 명령을 실행하세요: crontab -l"
echo "제거하려면 다음 명령을 실행하세요: crontab -e"
echo ""
