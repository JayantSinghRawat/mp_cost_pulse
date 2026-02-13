# How to Run MP Cost Pulse

## Option 1: Minimal stack (recommended first)

Runs only **Postgres + Backend + Frontend** (no Nginx, Airflow, or ML worker). Fewer images, faster build.

```bash
cd /home/bruhjeshhh/Work/mp_cost_pulse
docker-compose -f docker-compose.minimal.yml up -d --build
```

- **Frontend:** http://localhost:3000  
- **Backend API docs:** http://localhost:8000/docs  

If you see a Docker permission error (e.g. `permission denied` in `~/.docker`), fix it then retry:

```bash
sudo chown -R $USER:$USER ~/.docker
docker-compose -f docker-compose.minimal.yml up -d --build
```

---

## Option 2: Full stack

Runs everything (Postgres, Backend, Frontend, Nginx, Airflow, ML worker).

```bash
cd /home/bruhjeshhh/Work/mp_cost_pulse
docker-compose up -d --build
```

- **App via Nginx:** http://localhost  
- **Frontend (direct):** http://localhost:3000  
- **Backend API:** http://localhost:8000  
- **API docs:** http://localhost:8000/docs  
- **Airflow:** http://localhost:8080 (airflow / airflow)

---

## Option 3: Local dev (no Docker for app)

You need **Docker** (for Postgres with PostGIS) and **Python 3.11 + Node 18** on the host.

1. **Start only the database**
   ```bash
   docker run -d --name mpcostpulse-db \
     -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mpcostpulse \
     -p 5432:5432 postgis/postgis:15-3.3
   ```

2. **Backend**
   ```bash
   cd backend
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mpcostpulse
   pip install -r requirements.txt
   python -c "from app.core.database import init_db; init_db()"
   uvicorn main:app --reload --port 8000
   ```

3. **Frontend** (new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

- **Frontend:** http://localhost:3000  
- **API docs:** http://localhost:8000/docs  

---

## Useful commands

```bash
# Logs
docker-compose -f docker-compose.minimal.yml logs -f

# Stop minimal stack
docker-compose -f docker-compose.minimal.yml down

# Stop full stack
docker-compose down
```
