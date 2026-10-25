# WaterZero Dashboard

FastAPI backend plus a static frontend. The eight screens of the Figma "WaterZero" file (1440px canvas) are implemented one-to-one, with every value on screen coming from the API.

## Screens and routes

| Screen | Route | API endpoint | Source frame |
|---|---|---|---|
| Overview / Dashboard | `/` | `/api/dashboard` | 2:3 |
| Forecast | `/forecasts` | `/api/forecast` | 29:355 |
| Stress Test | `/stress-test` | `/api/stress-test` | 33:2 |
| Evidence & Verification | `/evidence` | `/api/evidence` | 38:2 |
| Model Health | `/model-health` | `/api/model-health` | 42:2 |
| Methodology | `/methodology` | `/api/methodology` | 147:11 |
| About Team | `/about-team` | `/api/about-team` | 110:2 |
| Reports | `/reports` | `/api/reports` | 150:2 |

`GET /api/health` returns a liveness check. Interactive API docs are at `/docs`.

## Layout

```
waterzero/
├── Dockerfile                    # one-step container build
├── README.md
└── backend/
    ├── requirements.txt
    ├── app/
    │   ├── main.py               # routes, API endpoints, page serving
    │   ├── schemas.py            # Overview contract
    │   ├── schemas_pages.py      # contracts for the seven other screens
    │   ├── data_source.py        # Overview data seam
    │   └── page_data.py          # data seam for the seven other screens
    └── static/
        ├── index.html            # Overview layout
        ├── page.html             # shared shell for the other screens
        ├── styles.css
        ├── app.js                # Overview rendering
        ├── wz-core.js            # shared page engine (elements, SVG helpers, loader)
        ├── pages/                # one layout file per screen
        └── img/                  # team portraits (see below)
```

## Run locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000.

## Run with Docker

```bash
docker build -t waterzero .
docker run -p 8000:8000 waterzero
```

The container reads `PORT` from the environment, so hosts that inject it (Render, Railway, Cloud Run, Fly.io) work without changes.

## Connecting real data

The frontend never reads data directly. Each screen gets its JSON from one endpoint, and each endpoint gets its data from one function.

| Screen | Replace this function | Contract |
|---|---|---|
| Overview | `get_dashboard()` in `app/data_source.py` | `DashboardResponse` in `app/schemas.py` |
| Forecast | `forecast()` in `app/page_data.py` | `ForecastResponse` |
| Stress Test | `stress_test()` | `StressTestResponse` |
| Evidence | `evidence()` | `EvidenceResponse` |
| Model Health | `model_health()` | `ModelHealthResponse` |
| Methodology | `methodology()` | `MethodologyResponse` |
| About Team | `about_team()` | `AboutTeamResponse` |
| Reports | `reports()` | `ReportsResponse` |

Each function returns a dict matching its contract. Pydantic validates the response, so a shape mismatch fails on the server instead of rendering wrong numbers. Start with the function for the screen you need first; the others keep their demo values.

Values the design marks as "Pending" or "—" are real states, not placeholders for missing code. When a measurement exists, return it in the same field and the layout fills in. Model Health and Evidence are designed to stay in their empty state until verified records are connected.

## Team portraits

The About Team page reads two photos from `backend/static/img/`:

- `team-leader.jpg` (Arohan Arora)
- `team-member.jpg` (Kunal Chawla)

Add the files there and they appear automatically. Without them the page shows the design's backdrop colour instead of breaking. The paths are set in `about_team()` in `app/page_data.py`.

## Running the API separately from the frontend

The frontend can be hosted on a different origin. Set the base URL before the page scripts load:

```html
<script>window.WATERZERO_API_BASE = "https://your-api.example.com";</script>
```

and add the frontend's origin to `CORS_ORIGINS` on the API (comma-separated; defaults to `*`).

## Adding a screen

1. Add its response model to `app/schemas_pages.py` and its data function to `app/page_data.py`.
2. Add the endpoint and route entry in `app/main.py`.
3. Create `static/pages/<key>.js` that registers `window.WZ_PAGES["<key>"]` with `w`, `h`, `api`, and a `build(data)` function. Use the `window.WZ` helpers (`R`, `T`, `C`, `topNav`) to describe positioned elements in Figma coordinates.
