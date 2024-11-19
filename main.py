from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from contextlib import asynccontextmanager

from scrapers.valorant_scraper import fetch_valorant_player_stats
from scrapers.cs2_scraper import fetch_cs2_player_stats
from models.valorant_model import ValorantPlayerStats
from models.cs2_model import CS2PlayerStats
from scrapers.tft_scraper import fetch_tft_player_stats
from models.tft_model import TFTPlayerStats

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY_HEADER = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_HEADER)

# TODO: Make API keys be stored in a DB
API_KEYS = set(os.getenv("API_KEYS", "").split(","))


async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key")


# Define a lifespan function for managing startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to manage app lifecycle events.
    """
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)

    # Initialize the rate limiter
    await FastAPILimiter.init(redis_client)
    yield  # Startup complete
    await redis_client.close()  # Shutdown cleanup


# Create the app with the lifespan parameter
app = FastAPI(lifespan=lifespan)


@app.get(
    "/valorant/player/{username}/current",
    response_model=ValorantPlayerStats,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_valorant_current_act_stats(
    username: str, api_key: str = Depends(get_api_key)
):
    player_stats = await fetch_valorant_player_stats(
        username=username, season="current"
    )
    if player_stats is None:
        raise HTTPException(
            status_code=404, detail=f"Player stats not found for username: {username}."
        )
    player_stats.season = "Current Act"
    return player_stats


@app.get(
    "/valorant/player/{username}/all",
    response_model=ValorantPlayerStats,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_valorant_all_seasons_stats(
    username: str, api_key: str = Depends(get_api_key)
):
    player_stats = await fetch_valorant_player_stats(username=username, season="all")
    if player_stats is None:
        raise HTTPException(
            status_code=404, detail=f"Player stats not found for username: {username}."
        )
    player_stats.season = "All Acts"
    return player_stats


@app.get(
    "/cs2/player/{steam_id}",
    response_model=CS2PlayerStats,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_cs2_stats(steam_id: str, api_key: str = Depends(get_api_key)):
    player_stats = await fetch_cs2_player_stats(steam_id=steam_id)
    if player_stats is None:
        raise HTTPException(
            status_code=404, detail=f"Player stats not found for steam_id: {steam_id}."
        )
    return player_stats


@app.get(
    "/tft/player/{username}",
    response_model=TFTPlayerStats,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_tft_player_stats(username: str, api_key: str = Depends(get_api_key)):
    player_stats = await fetch_tft_player_stats(username=username)
    if player_stats is None:
        raise HTTPException(
            status_code=404, detail=f"Player stats not found for username: {username}."
        )
    return player_stats


@app.get("/status", summary="API Health Check")
async def status():
    return {"status": "ok"}
