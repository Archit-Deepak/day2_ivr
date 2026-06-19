# IVR System (project4)

Flask + Plivo + Redis + Postgres IVR with menu, retry logic, and call history.

## Local Setup

### Prerequisites
- Python 3.8+
- Postgres running locally
- Redis running locally

### Steps

1. **Create and activate virtual environment**
   ```bash
   cd project4
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in:
   - `SECRET_KEY` — any random string (e.g. `openssl rand -hex 32`)
   - `PLIVO_AUTH_ID` — from [Plivo console](https://console.plivo.com) → Overview
   - `PLIVO_AUTH_TOKEN` — same page as above
   - `DATABASE_URL` — e.g. `postgresql://postgres:yourpassword@localhost:5432/ivr_db`
   - `REDIS_URL` — default `redis://localhost:6379` is fine if Redis is local
   - `PLIVO_NUMBER` — **leave blank** until the number is purchased and activated

4. **Create the Postgres database**
   ```bash
   createdb ivr_db
   ```
   (Replace `ivr_db` with whatever name you put in `DATABASE_URL`)

5. **Run database migrations**
   ```bash
   flask db init
   flask db migrate -m "init"
   flask db upgrade
   ```

6. **Start the server**
   ```bash
   python run.py
   ```
   Server runs on `http://localhost:5003`

---

## Endpoints

| Method | Route | Description |
|---|---|---|
| POST | `/ivr/welcome` | IVR entry point — returns menu XML |
| POST | `/ivr/handle-input` | Handles DTMF digit, branches logic |
| GET | `/call-history` | Returns call logs as JSON |

### `/call-history` query params
- `?limit=20` — number of results (default 20)
- `?from_number=+1xxxxxxxxxx` — filter by caller number
- `?selection=sales` — filter by menu selection (`sales`, `support`, `readback`, `invalid`, `timeout`)

---

## Quick Smoke Tests

```bash
# Check call history (should return [])
curl http://localhost:5003/call-history

# Simulate an inbound call hitting the welcome menu
curl -X POST http://localhost:5003/ivr/welcome

# Simulate pressing 1 (Sales)
curl -X POST http://localhost:5003/ivr/handle-input \
  -d "CallUUID=test-uuid-001&From=+14155551234&To=+14155559999&Digit=1"

# Confirm it was logged
curl "http://localhost:5003/call-history?selection=sales"
```

---

## IVR Flow

```
Inbound Call → POST /ivr/welcome → plays menu
                       │
              POST /ivr/handle-input
                       │
          ┌────────────┼────────────────┐
        1 │          2 │              3 │
       Sales        Support        Read back caller's number
          │          │                 │
          └──── all log to Postgres ───┘

  Invalid/no input → retry (max 3 via Redis) → Goodbye + Hangup
```
