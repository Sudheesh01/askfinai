# Finance AI Research App

A simple MVP that answers finance questions with real data and a strict LLM planner. No paid services, no mock data.

## Stack

- **Frontend**: Next.js + React + TypeScript + TailwindCSS + shadcn UI + ECharts
- **Backend**: FastAPI + pandas + numpy + yfinance + requests
- **LLM**: OpenRouter (model `qwen/qwen-2.5-vl-7b-instruct:free`)
- **News**: NewsAPI.org free tier
- **Cache**: in-memory dict
- **Watchlist**: `backend/watchlist.json`

## Environment Variables

### Backend (`backend/.env`)

```
OPENROUTER_API_KEY=your_openrouter_key
NEWS_API_KEY=your_newsapi_key
```

### Frontend (`frontend/.env.local`)

```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Run Locally

### Backend

```
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Deploy (Free)

### Render (backend)

1. Create a new **Web Service** on Render.
2. Connect the repo and set the root to `backend`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port 10000`
5. Add env vars:
   - `OPENROUTER_API_KEY`
   - `NEWS_API_KEY`
6. Use the free instance type.

### Vercel (frontend)

1. Import the repo into Vercel.
2. Set the root directory to `frontend`.
3. Add env var `NEXT_PUBLIC_BACKEND_URL` pointing to your Render URL.
4. Deploy with the free tier.

## Example Queries

- `current price of TCS`
- `show RSI for Reliance`
- `compare TCS vs Infosys fundamentals`
- `top 5 low volatility stocks`
- `summarize today’s market news`
- `show last 6 months chart`

## Notes

- The LLM **only** returns a JSON plan and summary. It never computes numbers.
- All prices and indicators are computed in the backend with deterministic math.
