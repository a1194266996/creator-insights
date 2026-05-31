#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/data/work/creator-insights}"
CONDA_SH="${CONDA_SH:-$HOME/miniconda3/etc/profile.d/conda.sh}"
CONDA_ENV="${CONDA_ENV:-myenv}"
CRON_TIME="${CRON_TIME:-30 8 * * *}"
LIMIT="${LIMIT:-20}"
DAYS="${DAYS:-7}"

mkdir -p "$PROJECT_DIR/logs"

JOB="$CRON_TIME cd $PROJECT_DIR && bash -lc 'source $CONDA_SH && conda activate $CONDA_ENV && python -m creator_insights daily --limit $LIMIT --days $DAYS >> logs/cron.log 2>&1'"

(crontab -l 2>/dev/null | grep -v "creator_insights daily"; echo "$JOB") | crontab -
echo "Installed cron job:"
echo "$JOB"
