from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from scraper import fetch_player_stats
from models import PlayerStats
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

API_KEY_HEADER = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_HEADER)

API_KEYS = set(os.getenv("API_KEYS", "").split(","))

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.get("/player/{username}/current", response_model=PlayerStats)
async def get_current_act_stats(username: str, api_key: str = Depends(get_api_key)):
    """
    Fetch the current act stats for a given Valorant player.
    """
    player_stats = await fetch_player_stats(username=username, season="current")
    if player_stats is None:
        raise HTTPException(status_code=404, detail="Player stats not found.")
    
    return player_stats

@app.get("/player/{username}/all", response_model=PlayerStats)
async def get_all_seasons_stats(username: str, api_key: str = Depends(get_api_key)):
    """
    Fetch all seasons' stats for a given Valorant player.
    """
    player_stats = await fetch_player_stats(username=username, season="all")
    if player_stats is None:
        raise HTTPException(status_code=404, detail="Player stats not found.")
    
    return player_stats
