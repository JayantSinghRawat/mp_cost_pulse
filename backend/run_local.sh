#!/usr/bin/env bash
# Run backend locally (no full Docker stack). Needs: Postgres with PostGIS on localhost:5432
set -e
cd "$(dirname "$0")"

echo "== MP Cost Pulse backend (local) =="

# 1) Start DB if you use Docker for just Postgres (run once):
#    docker run -d --name mpcostpulse-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mpcostpulse -p 5432:5432 postgis/postgis:15-3.3
#    Or: docker start mpcostpulse-db

# 2) Env
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/mpcostpulse}"

# 3) Venv + deps
if [ ! -d .venv ]; then
  echo "Creating venv..."
  python3 -m venv .venv
fi
echo "Installing deps (requirements-minimal.txt)..."
.venv/bin/pip install --prefer-binary -r requirements-minimal.txt

# 4) Check DB reachable then init
echo "Initializing DB..."
if ! .venv/bin/python -c "
from app.core.database import init_db
init_db()
print('DB ready')
"; then
  echo ""
  echo "DB init failed. Is Postgres running on localhost:5432?"
  echo "  Start it: docker run -d --name mpcostpulse-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mpcostpulse -p 5432:5432 postgis/postgis:15-3.3"
  echo "  Or: docker start mpcostpulse-db"
  exit 1
fi

# 5) Run API
echo ""
echo "Backend: http://127.0.0.1:8000   Docs: http://127.0.0.1:8000/docs"
exec .venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000
