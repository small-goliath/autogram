#!/usr/bin/env bash
# Render build script

set -o errexit

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install cryptography and its dependencies first with binary wheels only
pip install --only-binary=:all: cryptography==41.0.7 cffi==1.17.1

# Install remaining dependencies
pip install -r requirements.txt

# Run migrations
python -m alembic upgrade head

# Create admin account (will skip if already exists)
python scripts/create_admin.py || true
