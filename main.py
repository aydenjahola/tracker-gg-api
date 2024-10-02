from fastapi import FastAPI, HTTPException
from scraper import fetch_player_stats
from models import PlayerStats

app = FastAPI()

@app.get("/player/{username}/current", response_model=PlayerStats)
async def get_current_act_stats(username: str):
    """
    Fetch the current act stats for a given Valorant player.
    """
    player_stats = await fetch_player_stats(username=username, season="current")
    if player_stats is None:
        raise HTTPException(status_code=404, detail="Player stats not found.")
    
    return player_stats

@app.get("/player/{username}/all", response_model=PlayerStats)
async def get_all_seasons_stats(username: str):
    """
    Fetch all seasons' stats for a given Valorant player.
    """
    player_stats = await fetch_player_stats(username=username, season="all")
    if player_stats is None:
        raise HTTPException(status_code=404, detail="Player stats not found.")
    
    return player_stats