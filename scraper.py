import httpx
from bs4 import BeautifulSoup
from typing import Optional
from pydantic import BaseModel

class PlayerStats(BaseModel):
    username: str
    platform: str
    current_rank: Optional[str] = None
    peak_rank: Optional[str] = None
    level: Optional[int] = None
    kd_ratio: Optional[float] = None
    kills: Optional[int] = None
    wins: Optional[int] = None
    matches_played: Optional[int] = None
    headshot_percentage: Optional[float] = None
    win_percentage: Optional[float] = None

BASE_URL = "https://tracker.gg/valorant/profile/riot"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://tracker.gg/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

FLARESOLVERR_URL = "http://192.168.1.34:8191/"

async def fetch_player_stats(username: str, season: str = "current") -> Optional[PlayerStats]:
    url = f"{BASE_URL}/{username}/overview"
    if season == "all":
        url += "?season=all"

    payload = {
        "cmd": "request.get",
        "url": url,
        "maxTimeout": 60000,  
        "headers": HEADERS  
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(FLARESOLVERR_URL, json=payload)
            response.raise_for_status()  # Ensure we handle any errors

            page_content = response.json().get("solution", {}).get("response", "")

            if not page_content:
                print("No page content received.")
                return None

            soup = BeautifulSoup(page_content, "html.parser")

            # Current Rank
            current_rank_section = soup.find("div", class_="rating-entry__rank-info")
            current_rank = current_rank_section.find("div", class_="value").text.strip() if current_rank_section else "N/A"

            # Peak Rank
            peak_rank_section = current_rank_section.find_next("div", class_="rating-entry__rank-info")
            peak_rank = peak_rank_section.find("div", class_="value").text.strip() if peak_rank_section else "N/A"

            # K/D Ratio
            kd_ratio_section = soup.find('span', title="K/D Ratio")
            kd_ratio = kd_ratio_section.find_next('span', class_='value').text.strip() if kd_ratio_section else "0"

            # Kills
            kills_section = soup.find('span', title="Kills")
            if kills_section:
                kills_value = kills_section.find_parent('div', class_='numbers').find('span', class_='value')
                kills = kills_value.text.strip().replace(",", "") if kills_value else "0"
            else:
                kills = "0"

            # Wins
            wins_section = soup.find('span', title="Wins")
            wins = wins_section.find_next('span', class_='value').text.strip() if wins_section else "0"

            # Matches Played
            matches_section = soup.find('span', class_="matches")
            matches = matches_section.text.strip().replace("Matches", "").strip() if matches_section else "0"

            # Headshot Percentage
            headshot_section = soup.find('span', title="Headshot %")
            headshot_percentage = headshot_section.find_next('span', class_='value').text.strip().replace("%", "").strip() if headshot_section else "0.0"

            # Win Percentage
            win_section = soup.find('span', title="Win %")
            win_percentage = win_section.find_next('span', class_='value').text.strip().replace("%", "").strip() if win_section else "0.0"

            # Return parsed data as PlayerStats object
            return PlayerStats(
                username=username,
                platform="valorant",
                current_rank=current_rank,
                peak_rank=peak_rank,
                kd_ratio=float(kd_ratio) if kd_ratio.replace('.', '', 1).isdigit() else 0.0,  
                kills=int(kills) if kills.isdigit() else 0,  
                wins=int(wins) if wins.isdigit() else 0,
                matches_played=int(matches) if matches.isdigit() else 0,
                headshot_percentage=float(headshot_percentage) if headshot_percentage.replace('.', '', 1).isdigit() else 0.0,  
                win_percentage=float(win_percentage) if win_percentage.replace('.', '', 1).isdigit() else 0.0  
            )

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
