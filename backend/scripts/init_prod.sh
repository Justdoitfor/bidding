#!/bin/bash
set -e

echo "Starting production initialization..."

echo "1. Resetting database..."
uv run python scripts/reset_db.py

echo "2. Initializing admin and user accounts..."
uv run python init_db.py

echo "3. Importing real business data (100 rows per category)..."
uv run python scripts/import_real_data.py --dir /data --mode full --milvus-rebuild-index

echo "Initialization completed successfully!"
