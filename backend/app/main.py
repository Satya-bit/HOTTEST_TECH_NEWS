###
import os
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field


load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set.")
if not SERPAPI_API_KEY:
    raise RuntimeError("SERPAPI_API_KEY is not set.")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(title="News Summarizer API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummarizeRequest(BaseModel):
    query: Optional[str] = Field(
        default="hottest tech news",
        description="Search query for tech news.",
    )
    num_results: int = Field(default=8, ge=3, le=12)


class Article(BaseModel):
    title: str
    link: str
    source: Optional[str] = None
    date: Optional[str] = None
    icon: Optional[str] = None
    thumbnail: Optional[str] = None
    thumbnail_small: Optional[str] = None


class SummarizeResponse(BaseModel):
    query: str
    articles: List[Article]
    summary: str


def _fetch_news(query: str, num_results: int) -> List[Article]:
    params = {
        "engine": "google_news",
        "q": query,
        "hl": "en",
        "gl": "us",
        "num": num_results,
        "no_cache": "true",
        "api_key": SERPAPI_API_KEY,
    }
    resp = requests.get("https://serpapi.com/search.json", params=params, timeout=20)
    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"SerpApi error: {resp.status_code} {resp.text}",
        )
    data = resp.json()
    raw_results = data.get("news_results") or []
    articles: List[Article] = []
    for item in raw_results:
        title = item.get("title")
        link = item.get("link")
        if not title or not link:
            continue
        source = item.get("source")
        icon = None
        if isinstance(source, dict):
            icon = source.get("icon")
            source = source.get("name")
        articles.append(
            Article(
                title=title,
                link=link,
                source=source,
                date=item.get("date"),
                icon=icon,
                thumbnail=item.get("thumbnail"),
                thumbnail_small=item.get("thumbnail_small"),
            )
        )
    return articles


def _build_summary_prompt(articles: List[Article]) -> str:
    lines = []
    for idx, article in enumerate(articles, start=1):
        parts = [f"{idx}. {article.title}"]
        if article.source:
            parts.append(f"Source: {article.source}")
        if article.date:
            parts.append(f"Date: {article.date}")
        parts.append(f"Link: {article.link}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def _summarize_articles(articles: List[Article], max_bullets: int) -> str:
    if not articles:
        return "No relevant news articles were found."
    prompt = _build_summary_prompt(articles)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You summarize tech news in 9-10 lines. "
                    f"Provide exactly {max_bullets} bullet points, "
                    "each on its own line, "
                    "and keep it neutral and factual. Always keep the same order as the input list. "
                    "Use **bold** for the headline portion of each bullet."
                    "No bullet points in summary."
                ),
            },
            {
                "role": "user",
                "content": f"Summarize these articles:\n{prompt}",
            },
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest) -> SummarizeResponse:
    query = request.query or "latest technology news"
    articles = _fetch_news(query, request.num_results)
    summary = _summarize_articles(articles, min(len(articles), request.num_results))
    return SummarizeResponse(query=request.query or "latest technology news", articles=articles, summary=summary)


FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    def serve_index() -> FileResponse:
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{path:path}")
    def serve_spa(path: str) -> FileResponse:
        file_path = FRONTEND_DIST / path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
