import httpx
from typing import Optional
from models.cs2_model import CS2PlayerStats
from dotenv import load_dotenv
import os

load_dotenv()

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
CS2_APP_ID = "730"  # The App ID for CS2

async def fetch_steam_player_summary(steam_id: str) -> Optional[dict]:
    """Fetch basic player summary using the Steam API."""
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    if response.status_code == 200:
        data = response.json()
        if "response" in data and "players" in data["response"] and len(data["response"]["players"]) > 0:
            return data["response"]["players"][0]
    return None

async def fetch_cs2_user_stats(steam_id: str) -> Optional[list]:
    """Fetch CS2 user stats using the Steam API."""
    url = f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={CS2_APP_ID}&key={STEAM_API_KEY}&steamid={steam_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    if response.status_code == 200:
        data = response.json()
        if "playerstats" in data and "stats" in data["playerstats"]:
            return data["playerstats"]["stats"]
    return None

def get_stat_value(stats: list, stat_name: str) -> Optional[int]:
    """Helper function to extract a stat value by name from the stats list."""
    for stat in stats:
        if stat["name"] == stat_name:
            return stat["value"]
    return None

async def fetch_cs2_player_stats(steam_id: str) -> Optional[CS2PlayerStats]:
    player_summary = await fetch_steam_player_summary(steam_id)
    if not player_summary:
        print("No player summary found.")
        return None
    
    player_stats = await fetch_cs2_user_stats(steam_id)
    if not player_stats:
        print("No player stats found.")
        return None

    player_name = player_summary.get("personaname", "Unknown Player")

    stats_data = {stat["name"]: stat["value"] for stat in player_stats}
    
    total_deaths = stats_data.pop("total_deaths", 0)
    
    kills = stats_data.get("total_kills", 0)
    total_time_played = stats_data.get("total_time_played", 0)
    kd_ratio = kills / total_deaths if total_deaths > 0 else 0
    hours_played = total_time_played / 3600 if total_time_played else 0

    return CS2PlayerStats(
        steam_id=steam_id,
        platform="cs2",
        player_name=player_name,
        kd_ratio=round(kd_ratio, 2),
        kills=kills,
        total_deaths=total_deaths,
        hours_played=round(hours_played, 2),
        **stats_data
    )

