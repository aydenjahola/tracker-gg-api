from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import quote
from models.cs2_model import CS2PlayerStats
from flaresolverr_client import fetch_page_with_flaresolverr

CS2_BASE_URL = "https://tracker.gg/cs2/profile/steam"

async def fetch_cs2_player_stats(steam_id: str) -> Optional[CS2PlayerStats]:
    url = f"{CS2_BASE_URL}/{quote(steam_id)}/overview?playlist=premier"
        
    page_content = await fetch_page_with_flaresolverr(url)

    if not page_content:
        print("No page content received.")
        return None

    soup = BeautifulSoup(page_content, "html.parser")

    # Current rank
    current_rank_div = soup.find("div", class_="current-rank")
    if current_rank_div:
        current_rating_label = current_rank_div.find("label", class_="rating-emblem__label")
        current_rating_label = current_rating_label.text.strip() if current_rating_label else "Label not found"
    else:
        current_rating_label = "Current rank div not found"

    # Peak Rank
    peak_rank_div = soup.find("div", class_="p-4")
    if peak_rank_div:
        peak_rating_label = peak_rank_div.find("label", class_="rating-emblem__label")
        peak_rating_label = peak_rating_label.text.strip() if peak_rating_label else "Label not found"
        peak_tier = peak_rank_div.find("div", class_="text-18 font-medium")
        peak_tier = peak_tier.text.strip() if peak_tier else "Tier not found"
    else:
        peak_rating_label = "Peak rank div not found"
        peak_tier = "Tier not found"

    # K/D Ratio
    kd_ratio_section = soup.find('span', title="K/D Ratio")
    kd_ratio = kd_ratio_section.find_next('span', class_='value').text.strip() if kd_ratio_section else "0.0"

    # Matches Played
    matches_section = soup.find('span', class_="matches")
    matches_played = matches_section.text.strip().replace("Matches", "").strip() if matches_section else "0"
    matches_played = matches_played.replace(",", "")

    # Headshot Percentage
    headshot_section = soup.find('span', title="Headshot %")
    headshot_percentage = headshot_section.find_next('span', class_='value').text.strip().replace("%", "").strip() if headshot_section else "0.0"

    # Wins
    wins_section = soup.find('span', title="Wins")
    wins = wins_section.find_next('span', class_='value').text.strip().replace(",", "") if wins_section else "0"

    # Kills
    kills_section = soup.find('span', title="Kills")
    if kills_section:
        kills_value = kills_section.find_parent('div', class_='numbers').find('span', class_='value')
        kills = kills_value.text.strip().replace(",", "") if kills_value else "0"
    else:
        kills = "0"

    # Hours Played
    playtime_section = soup.find('span', class_='playtime')
    if playtime_section:
        hours_played_text = playtime_section.text.strip()
        hours_played = hours_played_text.split("h")[0].strip().replace(",", "") if "h" in hours_played_text else "0.0"
    else:
        hours_played = "0.0"

    # Win Percentage
    win_section = soup.find('span', title="Win %")
    win_percentage = win_section.find_next('span', class_='value').text.strip().replace("%", "").strip() if win_section else "0.0"

    # Tracker Score
    tracker_score_section = soup.find('div', class_="score__text")
    tracker_score = None
    if tracker_score_section:
        tracker_score_value = tracker_score_section.find('div', class_='value')
        tracker_score_text = tracker_score_value.text.strip().split()[0] if tracker_score_value else "0"
        tracker_score = int(tracker_score_text) if tracker_score_text.isdigit() else None

    return CS2PlayerStats(
        steam_id=steam_id,
        platform="cs2",
        current_rank=f"{current_rating_label}",
        peak_rank=f"{peak_rating_label} ({peak_tier})",
        kd_ratio=float(kd_ratio) if kd_ratio.replace('.', '', 1).isdigit() else 0.0,
        matches_played=int(matches_played) if matches_played.isdigit() else 0,
        headshot_percentage=float(headshot_percentage) if headshot_percentage.replace('.', '', 1).isdigit() else 0.0,
        wins=int(wins) if wins.isdigit() else 0,
        kills=int(kills) if kills.isdigit() else 0,
        hours_played=float(hours_played) if hours_played.replace('.', '', 1).isdigit() else 0.0,
        win_percentage=float(win_percentage) if win_percentage.replace('.', '', 1).isdigit() else 0.0,
        tracker_score=tracker_score
    )
