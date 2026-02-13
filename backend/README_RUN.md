# Run backend locally (no Docker stack)

## 1. Start the database

Postgres with PostGIS must be on `localhost:5432`.

**If you use Docker for Postgres:**

```bash
docker run -d --name mpcostpulse-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mpcostpulse -p 5432:5432 postgis/postgis:15-3.3
# or: docker start mpcostpulse-db
```

**If you have local Postgres (system) on 5432:** the app connects to that, not the container. Create the DB on the server that’s actually on `localhost:5432`:

```bash
# Create DB on whatever is listening on localhost:5432 (often system Postgres)
psql -U postgres -h localhost -d postgres -c "CREATE DATABASE mpcostpulse;"
# If that fails, try without -h (Unix socket): psql -U postgres -d postgres -c "CREATE DATABASE mpcostpulse;"
```

**“Database already exists” in Docker but app says it doesn’t:**  
Your app is using the Postgres on **localhost:5432**, which is probably **system Postgres**, not the container. Create the DB on that one (command above). To use the container instead, stop system Postgres so Docker can use port 5432: `sudo systemctl stop postgresql` (or equivalent), then `docker start mpcostpulse-db`.

## 2. Run the backend

```bash
cd backend
./run_local.sh
```

First run: creates `.venv`, installs from `requirements-minimal.txt`, inits DB, starts API.

- **API:** http://127.0.0.1:8000  
- **Docs:** http://127.0.0.1:8000/docs  
- **Health:** http://127.0.0.1:8000/health  

## If it didn’t work

**Paste the exact error** (from the terminal) so we can fix it. Common cases:

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named '...'` | Dependencies didn’t install. Run: `cd backend && .venv/bin/pip install -r requirements-minimal.txt` and see if pip prints an error. |
| `Failed building wheel for pydantic-core` or `psycopg2-binary` | Pip is building from source (no wheel for your platform). Try: `cd backend && .venv/bin/pip install --upgrade pip && .venv/bin/pip install --prefer-binary -r requirements-minimal.txt`. If it still fails, install build deps: Arch `sudo pacman -S postgresql-libs`, then retry. |
| `connection refused` / `could not connect to server` | DB not running. Run: `docker start mpcostpulse-db` (or the `docker run` above). |
| `Address already in use` (port 8000) | Something else is using 8000. Stop it or run: `uvicorn main:app --reload --port 8001` (and open http://127.0.0.1:8001/docs). |
| `permission denied` when running `./run_local.sh` | Run: `chmod +x backend/run_local.sh` then `./run_local.sh` again. |

**Manual run (same result as the script):**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-minimal.txt
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mpcostpulse
python -c "from app.core.database import init_db; init_db()"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
