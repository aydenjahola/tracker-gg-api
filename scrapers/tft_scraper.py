from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import quote
from models.tft_model import TFTPlayerStats
from flaresolverr_client import fetch_page_with_flaresolverr

BASE_URL = "https://tracker.gg/tft/profile/riot"


async def fetch_tft_player_stats(username: str) -> Optional[TFTPlayerStats]:
    url = f"{BASE_URL}/{quote(username)}/overview"

    # Fetch the page content using the centralized FlareSolverr client
    page_content = await fetch_page_with_flaresolverr(url)

    if not page_content:
        print("No page content received.")
        return None

    soup = BeautifulSoup(page_content, "html.parser")

    # Rank
    rank_section = soup.find("div", class_="highlighted-stat--progression")
    rank = "Unknown"
    lp = "0"

    if rank_section:
        rank_text = rank_section.find("div", class_="highlight-text")
        if rank_text:
            rank = rank_text.text.strip()

        lp_section = rank_section.find("span", class_="progression")
        if lp_section:
            lp_text = (
                lp_section.text.strip()
                .replace("Tier Progress: ", "")
                .replace(" LP", "")
            )
            lp = lp_text.strip().replace(",", "")

    # Wins
    wins_section = soup.find("span", title="Wins")
    wins = (
        wins_section.find_next("span", class_="value").text.strip().replace(",", "")
        if wins_section
        else "0"
    )

    # Losses
    losses_section = soup.find("span", title="Losses")
    losses = (
        losses_section.find_next("span", class_="value").text.strip().replace(",", "")
        if losses_section
        else "0"
    )

    # Win Percentage
    win_percentage_section = soup.find("span", title="Win %")
    win_percentage = (
        win_percentage_section.find_next("span", class_="value")
        .text.strip()
        .replace("%", "")
        .strip()
        if win_percentage_section
        else "0.0"
    )

    # Matches Played
    matches_section = soup.find("span", title="Matches Played")
    matches_played = (
        matches_section.find_next("span", class_="value").text.strip().replace(",", "")
        if matches_section
        else "0"
    )

    return TFTPlayerStats(
        username=username,
        platform="tft",
        current_rank=rank,
        lp=int(lp) if lp.isdigit() else 0,
        wins=int(wins) if wins.isdigit() else 0,
        losses=int(losses) if losses.isdigit() else 0,
        win_percentage=float(win_percentage)
        if win_percentage.replace(".", "", 1).isdigit()
        else 0.0,
        matches_played=int(matches_played) if matches_played.isdigit() else 0,
    )
