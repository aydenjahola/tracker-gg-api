import re
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import quote
from models.valorant_model import ValorantPlayerStats, Weapon, MapStats, Role
from flaresolverr_client import fetch_page_with_flaresolverr

BASE_URL = "https://tracker.gg/valorant/profile/riot"


async def fetch_valorant_player_stats(
    username: str, season: str = "current"
) -> Optional[ValorantPlayerStats]:
    url = f"{BASE_URL}/{quote(username)}/overview"
    if season == "all":
        url += "?season=all"

    # Fetch the page content using the centralized FlareSolverr client
    page_content = await fetch_page_with_flaresolverr(url)

    if not page_content:
        print("No page content received.")
        return None

    soup = BeautifulSoup(page_content, "html.parser")

    # Current Rank and Level
    current_rank = "Unknown"
    level = None
    rating_section = soup.find("div", class_="trn-profile-highlighted-content__stats")
    if rating_section:
        rank_img = rating_section.find(
            "img", class_="trn-profile-highlighted-content__icon"
        )
        if rank_img:
            current_rank = rank_img.get("alt", "Unknown").strip()
        level_div = rating_section.find("div", class_="stat")
        if (
            level_div
            and level_div.find("span", class_="stat__label").text.strip() == "Level"
        ):
            level_text = level_div.find("span", class_="stat__value").text.strip()
            level = int(level_text) if level_text.isdigit() else None

    # Peak Rank
    peak_rank_section = soup.find(
        "div", class_="rating-summary__content rating-summary__content--secondary"
    )
    peak_rank = "Unknown"
    peak_rank_episode = "N/A"
    if peak_rank_section:
        peak_rank_info = peak_rank_section.find("div", class_="rating-entry__rank-info")
        if peak_rank_info:
            peak_rank_value = peak_rank_info.find("div", class_="value").text.strip()
            peak_rank = f"{peak_rank_value}".strip()
            episode_act_div = peak_rank_info.find("div", class_="subtext")
            peak_rank_episode = (
                episode_act_div.text.strip() if episode_act_div else "N/A"
            )

    # Tracker Score
    tracker_score_section = soup.find("div", class_="performance-score__container")
    tracker_score = None
    round_win_percentage = None
    if tracker_score_section:
        score_value = tracker_score_section.find("div", class_="value")
        if score_value:
            tracker_score_text = score_value.text.strip().split("/")[0]
            tracker_score = (
                int(tracker_score_text) if tracker_score_text.isdigit() else None
            )
        # Round Win %
        stats = tracker_score_section.find_all("div", class_="stat")
        for stat in stats:
            label = stat.find("div", class_="stat__label").text.strip()
            value = stat.find("div", class_="stat__value").text.strip().replace("%", "")
            if label == "Round Win %":
                round_win_percentage = float(value)

    # Playtime and Matches Played
    title_stats = soup.find("div", class_="title-stats")
    playtime_hours = 0.0
    matches_played = 0
    if title_stats:
        playtime_span = title_stats.find("span", class_="playtime")
        if playtime_span:
            playtime_text = playtime_span.text.strip()
            match = re.search(r"([\d\.]+)h", playtime_text)
            if match:
                playtime_hours = float(match.group(1))
        matches_span = title_stats.find("span", class_="matches")
        if matches_span:
            matches_text = matches_span.text.strip()
            match = re.search(r"(\d+)", matches_text)
            if match:
                matches_played = int(match.group(1))

    # Main Stats
    stats_sections = soup.find_all("div", class_="stat")
    stats_dict = {}
    for stat in stats_sections:
        name_span = stat.find("span", class_="name")
        if not name_span:
            continue
        stat_name = name_span.get("title", "").strip()
        value_span = stat.find("span", class_="value")
        if value_span:
            value_text = value_span.text.strip().replace("%", "").replace(",", "")
            stats_dict[stat_name] = value_text

    # Extract individual stats
    damage_per_round = float(stats_dict.get("Damage/Round", 0.0))
    kd_ratio = float(stats_dict.get("K/D Ratio", 0.0))
    headshot_percentage = float(stats_dict.get("Headshot %", 0.0))
    win_percentage = float(stats_dict.get("Win %", 0.0))
    wins = int(stats_dict.get("Wins", 0))
    kast = float(stats_dict.get("KAST", 0.0))
    ddr_per_round = float(stats_dict.get("DDΔ/Round", 0.0))
    kills = int(stats_dict.get("Kills", 0))
    deaths = int(stats_dict.get("Deaths", 0))
    assists = int(stats_dict.get("Assists", 0))
    acs = float(stats_dict.get("ACS", 0.0))
    kad_ratio = float(stats_dict.get("KAD Ratio", 0.0))
    kills_per_round = float(stats_dict.get("Kills/Round", 0.0))
    first_bloods = int(stats_dict.get("First Bloods", 0))
    flawless_rounds = int(stats_dict.get("Flawless Rounds", 0))
    aces = int(stats_dict.get("Aces", 0))

    # Extract top weapons
    top_weapons = []
    weapons_section = soup.find("div", class_="top-weapons__content")
    if weapons_section:
        weapon_divs = weapons_section.find_all("div", class_="weapon")
        for weapon_div in weapon_divs:
            name_div = weapon_div.find("div", class_="weapon__name")
            type_div = weapon_div.find("div", class_="weapon__type")
            silhouette_img = weapon_div.find("img", class_="weapon__silhouette")
            accuracy_hits_div = weapon_div.find("div", class_="weapon__accuracy-hits")
            main_stat_div = weapon_div.find("div", class_="weapon__main-stat")

            if (
                name_div
                and type_div
                and silhouette_img
                and accuracy_hits_div
                and main_stat_div
            ):
                weapon_name = name_div.text.strip()
                weapon_type = type_div.text.strip()
                silhouette_url = silhouette_img["src"]
                accuracy = [
                    stat.text.strip()
                    for stat in accuracy_hits_div.find_all("span", class_="stat")
                ]
                kills = int(
                    main_stat_div.find("span", class_="value")
                    .text.replace(",", "")
                    .strip()
                )

                top_weapons.append(
                    Weapon(
                        name=weapon_name,
                        weapon_type=weapon_type,
                        silhouette_url=silhouette_url,
                        accuracy=accuracy,
                        kills=kills,
                    )
                )

    # Extract top maps
    top_maps = []
    top_maps_section = soup.find("div", class_="top-maps__maps")
    if top_maps_section:
        map_divs = top_maps_section.find_all("div", class_="top-maps__maps-map")
        for map_div in map_divs:
            name_div = map_div.find("div", class_="name")
            info_div = map_div.find("div", class_="info")
            if name_div and info_div:
                map_name = name_div.text.strip()
                win_percentage = (
                    info_div.find("div", class_="value").text.replace("%", "").strip()
                )
                matches = info_div.find("div", class_="label").text.strip()
                top_maps.append(
                    MapStats(
                        name=map_name, win_percentage=win_percentage, matches=matches
                    )
                )

    # Extract roles
    roles = []
    roles_section = soup.find("div", class_="roles__list")
    if roles_section:
        role_divs = roles_section.find_all("div", class_="role")
        for role_div in role_divs:
            role_name = role_div.find("h5", class_="role__name").text.strip()
            role_stats = role_div.find("div", class_="role__stats")
            if role_stats:
                # Win rate
                win_rate_text = role_stats.find(
                    "span", class_="role__value"
                ).text.strip()
                win_rate = win_rate_text.replace("%", "").split(" ")[1]

                # Wins and Losses
                win_loss_text = role_stats.find("span", class_="role__sub").text.strip()
                wins, losses = map(int, re.findall(r"\d+", win_loss_text))

                # KDA
                kda_text = role_stats.find_all("span", class_="role__value")[
                    1
                ].text.strip()
                kda = float(kda_text.split(" ")[1])

                # Kills, Deaths, and Assists
                kd_stats = role_stats.find_all("span", class_="role__sub")[
                    1
                ].text.strip()
                kills, deaths, assists = map(int, re.findall(r"\d+", kd_stats))

                roles.append(
                    Role(
                        name=role_name,
                        win_rate=win_rate,
                        wins=wins,
                        losses=losses,
                        kda=kda,
                        kills=kills,
                        deaths=deaths,
                        assists=assists,
                    )
                )

    return ValorantPlayerStats(
        username=username,
        platform="valorant",
        season="All",
        current_rank=current_rank,
        peak_rank=peak_rank,
        level=level,
        tracker_score=tracker_score,
        round_win_percentage=round_win_percentage,
        playtime_hours=playtime_hours,
        matches_played=matches_played,
        damage_per_round=damage_per_round,
        kd_ratio=kd_ratio,
        headshot_percentage=headshot_percentage,
        win_percentage=win_percentage,
        wins=wins,
        kast=kast,
        ddr_per_round=ddr_per_round,
        kills=kills,
        deaths=deaths,
        assists=assists,
        acs=acs,
        kad_ratio=kad_ratio,
        kills_per_round=kills_per_round,
        first_bloods=first_bloods,
        flawless_rounds=flawless_rounds,
        aces=aces,
        top_weapons=top_weapons,
        top_maps=top_maps,
        roles=roles,
    )
