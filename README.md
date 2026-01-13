# Tech News Summarizer

A FastAPI + React (Vite) app that fetches hot tech news with SerpApi and summarizes it with OpenAI.

## How to run locally

### Backend (FastAPI)
1. Create a virtual environment and install dependencies:
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Copy environment variables:
   ```bash
   copy .env.example .env
   ```
3. Set your keys in `backend/.env`:
   - `OPENAI_API_KEY`
   - `SERPAPI_API_KEY`
   - Optional: `OPENAI_MODEL` (default `gpt-4o-mini`)
4. Run the API:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend (Vite React)
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Optional: set API base URL (defaults to `http://localhost:8000`):
   ```bash
   copy .env.example .env
   ```
   Then edit `frontend/.env` if you want a different API URL.
3. Run the frontend:
   ```bash
   npm run dev
   ```

## API usage
- `POST /api/summarize`
  - Body: `{ "query": "hottest technology news", "num_results": 8 }`
  - Response includes `summary` and `articles`.

## Approach & tradeoffs
- Fetches news via SerpApi `google_news` and passes headlines to OpenAI for summarization.
- Keeps the flow single‑request for speed and simplicity.
- Tradeoff: No deduping or clustering beyond SerpApi results.
- Tradeoff: No agent framework yet (lighter dependencies and lower latency).

## AI tools used
- OpenAI API (`chat.completions`) for summarizing the news list into bullet points.
- Codex for assisting when developing frontend(especially CSS).