#!/usr/bin/env bash
# Render build script

set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install wheel to use pre-built binaries
pip install wheel

# Install dependencies
pip install -r requirements.txt

# Run migrations
python -m alembic upgrade head

# Create admin account (will skip if already exists)
python scripts/create_admin.py || true
