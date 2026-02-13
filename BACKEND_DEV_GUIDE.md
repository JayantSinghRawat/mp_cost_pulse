# Backend developer guide — MP Cost Pulse

You’re working on the **API backend** for **MP Cost Pulse**: cost-of-living and real-estate data for Madhya Pradesh (rent, groceries, transport, inflation, maps, ML predictions). This doc is what you need to work effectively on the backend.

---

## 1. What this backend is

- **Framework:** FastAPI
- **DB:** PostgreSQL with **PostGIS** (geospatial)
- **ORM:** SQLAlchemy 2.x
- **Auth:** JWT (OAuth2 Bearer) + optional 2FA (OTP by email)
- **API surface:** REST under `/api/v1/`; OpenAPI at `/docs`

It serves the React frontend and can be used by other clients. Some ML (XGBoost cost predictor, DistilBERT rent classifier) runs in this process or in a separate ML worker; the API calls into that via `app/ml/` and `app/services/ml_service.py`.

---

## 2. Project layout (what lives where)

```
backend/
├── main.py                 # FastAPI app, CORS, mount /api/v1
├── requirements.txt
├── init_db.sql             # PostGIS extensions (tables created by Python)
├── app/
│   ├── core/               # Config, DB, security — no routes
│   │   ├── config.py       # Pydantic Settings (env, secrets)
│   │   ├── database.py     # Engine, SessionLocal, get_db, init_db
│   │   └── security.py     # bcrypt, JWT create/decode
│   ├── api/v1/             # All HTTP entrypoints
│   │   ├── router.py       # Aggregates all routers
│   │   ├── auth.py         # /auth/register, login, login-json, verify-otp, me
│   │   ├── rents.py        # /rents/
│   │   ├── groceries.py    # /groceries/
│   │   ├── transport.py    # /transport/
│   │   ├── inflation.py    # /inflation/
│   │   ├── geospatial.py   # /geospatial/
│   │   ├── ml.py           # /ml/predict-cost, classify-rent, models
│   │   ├── recommendations.py
│   │   └── scraping.py
│   ├── models/             # SQLAlchemy ORM (DB tables)
│   ├── schemas/            # Pydantic (request/response)
│   ├── services/           # Business logic (used by api/v1)
│   └── ml/                 # Cost predictor & rent classifier (load/save models)
```

**Convention:** Routes are thin: they validate input (Pydantic), call a **service**, return **schemas**. No business logic in `api/`; no DB or HTTP in `models/` or `schemas/`.

---

## 3. Request flow (pattern per feature)

For a typical feature (e.g. rents):

1. **Route** (`app/api/v1/rents.py`)  
   - Defines `APIRouter(prefix="/rents", tags=["rents"])`.  
   - Uses `Depends(get_db)` for a DB session and optionally `Depends(get_current_user)` for auth.  
   - Parses query/body via Pydantic (or `Query()`).  
   - Calls **one** method on the corresponding **service**.

2. **Service** (`app/services/rent_service.py`)  
   - Class with `@staticmethod` methods.  
   - Takes `db: Session` and other typed args.  
   - Uses **models** (e.g. `RentListing`, `Locality`) for queries and commits.  
   - Returns ORM instances or dicts.

3. **Models** (`app/models/rent.py`, etc.)  
   - SQLAlchemy `Base` classes, table names, columns, relationships.  
   - Geospatial: `geoalchemy2.Geometry` (e.g. `Locality.geometry`).

4. **Schemas** (`app/schemas/rent.py`)  
   - Pydantic `BaseModel`: `*Create` for POST body, `*Response` for JSON out.  
   - Use `response_model=` on routes so FastAPI serializes correctly.  
   - `from_attributes = True` when the response is an ORM instance.

Example (simplified):

```python
# api/v1/rents.py
@router.get("/", response_model=List[RentListingResponse])
def get_rent_listings(locality_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    return RentService.get_listings(db=db, locality_id=locality_id, ...)

# services/rent_service.py
def get_listings(db, locality_id=None, ...):
    query = db.query(RentListing)
    if locality_id:
        query = query.filter(RentListing.locality_id == locality_id)
    return query.offset(skip).limit(limit).all()
```

---

## 4. Auth: what you must know

- **Login for the frontend:**  
  - POST `/api/v1/auth/login-json` with `{ "username", "password" }` → returns `session_token` and “OTP sent”.  
  - POST `/api/v1/auth/verify-otp` with `{ "session_token", "otp_code" }` → returns `access_token` (JWT).  
  - So the app uses **2FA (OTP by email)** for login.

- **Classic OAuth2 (e.g. for scripts):**  
  - POST `/api/v1/auth/login` with form `username` + `password` → returns JWT (no OTP).

- **JWT payload:**  
  - `sub`: username (str)  
  - `user_id`: user id (int)  
  - `exp`: expiry  

- **Protecting a route:**  
  - Use `get_current_user` (returns full `User`) or `get_current_user_id` (returns `user_id`).  
  - Example (from `auth.py`):  
    `def get_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db))` then decode token and load user.  
  - Example (from `ml.py`):  
    `user_id: int = Depends(get_current_user_id)` for endpoints that only need the id.

- **OAuth2 scheme:**  
  - `OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")` — send header: `Authorization: Bearer <access_token>`.

- **Where it’s used:**  
  - `/auth/me` and `/ml/*` (e.g. predict-cost) require a valid token. Many read-only APIs (rents, groceries, etc.) do **not** require auth.

---

## 5. Config and environment

- **Source:** `app/core/config.py` uses **pydantic-settings** with `env_file = ".env"`. Env vars override defaults.

- **Important variables:**
  - `DATABASE_URL` — e.g. `postgresql://postgres:postgres@postgres:5432/mpcostpulse` (default assumes Docker service name `postgres`).
  - `SECRET_KEY` — **must** be set in production for JWT signing.
  - `CORS_ORIGINS` — list of allowed origins (default includes localhost:3000, 5173).
  - SMTP (e.g. `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL`) — used to send OTP emails.
  - Optional API keys: `MAPBOX_ACCESS_TOKEN`, `GOOGLE_PLACES_API_KEY`, `BIGBASKET_API_KEY`, etc.

- **Security:** Do **not** commit real secrets. In production, set `SECRET_KEY` and SMTP (and any API keys) via env; consider moving SMTP out of default values in code.

---

## 6. Database (PostgreSQL + PostGIS)

- **Engine/session:**  
  - One global `engine` and `SessionLocal` in `app/core/database.py`.  
  - Routes get a session with `get_db()` (yielded, so it’s closed after request).

- **Init (tables + PostGIS):**  
  - `init_db()` in `database.py`: enables PostGIS, then `Base.metadata.create_all(bind=engine)`.  
  - All models must be imported so they’re registered on `Base` (see `init_db()` imports).  
  - Docker/startup often runs:  
    `python -c "from app.core.database import init_db; init_db()"`  
    before starting uvicorn.

- **Models to know:**  
  - `User`, `OTP` — auth.  
  - `Locality`, `LocalityStats` — geography (PostGIS geometry on `Locality`).  
  - `RentListing` — rent listings; FK to `Locality`.  
  - `GroceryStore`, `GroceryItem`, `TransportRoute`, `TransportFare`, `InflationData` — cost data.  
  - `MLModelVersion`, `Prediction` — ML metadata and prediction history.  
  - `NeighborhoodData` — neighborhood/amenity data.  

- **Changing schema:**  
  - Add/migrate tables or columns via new SQLAlchemy models (or Alembic if you introduce it). After changing models, re-run `init_db()` only if you’re still in “create_all” mode; in production you’d use migrations.

---

## 7. Adding a new feature (checklist)

1. **Model** in `app/models/<domain>.py` (and export in `app/models/__init__.py` if you use it in `init_db` or elsewhere).
2. **Schemas** in `app/schemas/<domain>.py` (e.g. `FooCreate`, `FooResponse`).
3. **Service** in `app/services/<domain>_service.py` (static methods taking `db` and domain args).
4. **Router** in `app/api/v1/<domain>.py` (prefix, tags, `Depends(get_db)`, optional `Depends(get_current_user)` or `get_current_user_id`).
5. **Register router** in `app/api/v1/router.py`:  
   `api_router.include_router(<module>.router)`.

Then the new routes are under `/api/v1/<prefix>/...` and show up in `/docs`.

---

## 8. Running and testing the backend

- **With Docker (minimal stack):**  
  From repo root:  
  `docker-compose -f docker-compose.minimal.yml up -d`  
  Backend is on port 8000.

- **Local (no Docker for app):**  
  1. Postgres with PostGIS (e.g. Docker):  
     `docker run -d -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mpcostpulse -p 5432:5432 postgis/postgis:15-3.3`  
  2. In `backend/`:  
     - `export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mpcostpulse`  
     - `pip install -r requirements.txt`  
     - `python -c "from app.core.database import init_db; init_db()"`  
     - `uvicorn main:app --reload --port 8000`  

- **Health:**  
  - GET `http://localhost:8000/health` → `{"status":"healthy"}`  
  - GET `http://localhost:8000/docs` → Swagger UI.

- **Testing:**  
  - Use `/docs` to call endpoints.  
  - For protected routes, use “Authorize” with `Bearer <access_token>` (from `/auth/login` or `/auth/verify-otp`).

---

## 9. Handy scripts in `backend/`

- `seed_bhopal_localities.py`, `seed_mp_cities.py` — seed localities/cities.  
- `create_bhopal_neighborhood_data.py`, `refresh_bhopal_places_data.py`, `refresh_all_neighborhoods.py` — neighborhood/places data.  
- `create_missing_stats.py`, `update_stats_from_scraped_data.py` — locality stats.  
- `scrape_bhopal.py` — scraping.  

Run them with the same `DATABASE_URL` and Python env as the API (and with PostGIS DB up).

---

## 10. Quick reference

| You want to…                    | Look at / use |
|---------------------------------|---------------|
| Add a new API domain            | `api/v1/<name>.py` + `router.py` |
| Change DB tables                | `models/`, then `init_db` or migrations |
| Change request/response shape   | `schemas/` |
| Implement business logic       | `services/` |
| Auth (who is logged in)         | `Depends(get_current_user)` or `get_current_user_id` |
| Config / env                    | `app/core/config.py`, `.env` |
| DB session                      | `Depends(get_db)` |
| JWT / passwords                 | `app/core/security.py` |
| ML (cost prediction, classify) | `app/ml/`, `app/services/ml_service.py`, `api/v1/ml.py` |

---

That’s the backend in one place. Use `/docs` and this guide to navigate and extend the API.
