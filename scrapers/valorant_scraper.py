from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import quote
from models.valorant_model import ValorantPlayerStats
from flaresolverr_client import fetch_page_with_flaresolverr

BASE_URL = "https://tracker.gg/valorant/profile/riot"

async def fetch_valorant_player_stats(username: str, season: str = "current") -> Optional[ValorantPlayerStats]:
    url = f"{BASE_URL}/{quote(username)}/overview"
    if season == "all":
        url += "?season=all"

    # Fetch the page content using the centralized FlareSolverr client
    page_content = await fetch_page_with_flaresolverr(url)

    if not page_content:
        print("No page content received.")
        return None

    soup = BeautifulSoup(page_content, "html.parser")

    # Current Rank
    current_rank_section = soup.find("div", class_="rating-summary__content")
    current_rank = "Unknown"
    if current_rank_section:
        rank_info = current_rank_section.find("div", class_="rating-entry__rank-info")
        if rank_info:
            current_rank_label = rank_info.find("div", class_="label").text.strip()
            current_rank_value = rank_info.find("div", class_="value").text.strip()
            current_rank_rr = rank_info.find("span", class_="mmr")
            current_rank = f"{current_rank_label} {current_rank_value}".strip() if current_rank_rr else current_rank_value

    # Peak Rank
    peak_rank_section = soup.find("div", class_="rating-summary__content rating-summary__content--secondary")
    peak_rank = "Unknown"
    peak_rank_episode = "N/A"
    if peak_rank_section:
        peak_rank_info = peak_rank_section.find("div", class_="rating-entry__rank-info")
        if peak_rank_info:
            peak_rank_value = peak_rank_info.find("div", class_="value").text.strip()
            peak_rank = f"{peak_rank_value}".strip()
            episode_act_div = peak_rank_info.find("div", class_="subtext")
            peak_rank_episode = episode_act_div.text.strip() if episode_act_div else "N/A"

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
    wins = wins_section.find_next('span', class_='value').text.strip().replace(",", "") if wins_section else "0"

    # Matches Played
    matches_section = soup.find('span', class_="matches")
    matches = matches_section.text.strip().replace("Matches", "").strip() if matches_section else "0"
    matches = matches.replace(",", "")

    # Headshot Percentage
    headshot_section = soup.find('span', title="Headshot %")
    headshot_percentage = headshot_section.find_next('span', class_='value').text.strip().replace("%", "").strip() if headshot_section else "0.0"

    # Win Percentage
    win_section = soup.find('span', title="Win %")
    win_percentage = win_section.find_next('span', class_='value').text.strip().replace("%", "").strip() if win_section else "0.0"

    # Hours Played
    playtime_section = soup.find('span', class_='playtime')
    hours_played = "0.0"
    if playtime_section:
        hours_played_text = playtime_section.text.strip()
        hours_played = hours_played_text.split("h")[0].strip().replace(",", "") if "h" in hours_played_text else "0.0"

    # Tracker Score
    tracker_score_section = soup.find('div', class_="score__text")
    tracker_score = None
    if tracker_score_section:
        tracker_score_value = tracker_score_section.find('div', class_='value')
        tracker_score_text = tracker_score_value.text.strip().split()[0] if tracker_score_value else ""
        tracker_score = int(tracker_score_text) if tracker_score_text.isdigit() else None

    # ACS (Average Combat Score)
    acs_section = soup.find('span', title="ACS")
    acs_value = acs_section.find_next('span', class_='value').text.strip() if acs_section else "0.0"

    return ValorantPlayerStats(
        username=username,
        platform="valorant",
        current_rank=current_rank,
        peak_rank=peak_rank,
        peak_rank_episode=peak_rank_episode,
        kd_ratio=float(kd_ratio) if kd_ratio.replace('.', '', 1).isdigit() else 0.0,
        kills=int(kills) if kills.isdigit() else 0,
        wins=int(wins) if wins.isdigit() else 0,
        matches_played=int(matches) if matches.isdigit() else 0,
        headshot_percentage=float(headshot_percentage) if headshot_percentage.replace('.', '', 1).isdigit() else 0.0,
        win_percentage=float(win_percentage) if win_percentage.replace('.', '', 1).isdigit() else 0.0,
        hours_played=float(hours_played) if hours_played.replace('.', '', 1).isdigit() else 0.0,
        tracker_score=tracker_score,
        acs=float(acs_value) if acs_value.replace('.', '', 1).isdigit() else 0.0
    )
